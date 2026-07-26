"""
app.py — Flask application factory, configuration, and all routes.

Security checklist per route:
    - Every POST is CSRF-protected via Flask-WTF.
    - Every task/priority lookup asserts user_id == current_user.id.
    - No naive local-time datetimes are written to DB (only naive UTC).
    - Passwords are never logged or returned in responses.
    - Jinja2 auto-escaping is always on (no | safe on user content).

Delta changes:
    - inject_user_prefs context processor added for lang/date_format globals
    - /settings GET+POST route added
    - priority_create/priority_delete redirect to /settings instead of /
    - utc_naive_to_jalali_str calls now pass date_format and language from context
"""

# =====================================================================
# FILE: app.py
# PURPOSE: Flask application factory, configuration, and all routes.
# =====================================================================

import os
import re

PASSWORD_REGEX = re.compile(r"^[A-Za-z0-9&!@#$%]+$")

from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf
from sqlalchemy import and_, case, or_

from forms import (
    CSRFForm,
    CustomPriorityForm,
    EditTaskForm,
    LoginForm,
    RegisterForm,
    SettingsForm,
    TaskForm,
)
from translations import get_translations, get_localized_priorities
from models import CustomPriority, Task, User, db
from utils import (
    DEFAULT_PRIORITIES,
    get_custom_range_utc,
    get_daily_range_utc,
    get_monthly_range_utc,
    get_task_status_python,
    get_weekly_range_utc,
    get_yearly_range_utc,
    jalali_str_to_utc_naive,
    localize_digits,
    utc_naive_to_jalali_str,
)

# ---------------------------------------------------------------------
# ⬛ ENVIRONMENT SETUP: Load .env file for configuration secrets
# ---------------------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------------------
# ⬛ APPLICATION FACTORY: Flask app creation and configuration
# ---------------------------------------------------------------------


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # --- ▷ Core Config ---
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Copy .env.example to .env and set a strong secret key."
        )
    app.config["SECRET_KEY"] = secret_key

    # --- ▷ Database Config ---
    db_url = os.environ.get("DATABASE_URL", "sqlite:///instance/todo.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- ▷ Session Config ---
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # --- ▷ CSRF Config ---
    app.config["WTF_CSRF_ENABLED"] = True

    # --- ▷ Disable static-file caching in development ---
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    # --- ▷ Extensions ---
    db.init_app(app)
    bcrypt = Bcrypt(app)
    csrf = CSRFProtect(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message = ""  # handled dynamically below
    login_manager.login_message_category = "warning"

    @login_manager.unauthorized_handler
    def unauthorized():
        flash(_t("flash_login_required"), "warning")
        return redirect(url_for("login"))

    # Helper: look up a flash message key in the current user's language.
    # For authenticated users reads current_user.language.
    # For unauthenticated users reads session['anon_lang'] (set by /set-lang or logout).
    def _t(key, **kwargs):
        if current_user.is_authenticated:
            lang = current_user.language
        else:
            lang = session.get('anon_lang', 'fa')
        val = get_translations(lang).get(key, key)
        return val.format(**kwargs) if kwargs else val

    # --- ▷ User Loader ---
    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Make common helpers and user prefs available in all templates
    @app.context_processor
    def inject_globals():
        def static_version(filename):
            """Return mtime of a static file for cache-busting via ?v=<mtime>."""
            try:
                path = os.path.join(app.static_folder, filename)
                return int(os.path.getmtime(path))
            except OSError:
                return 0

        return {
            "csrf_token": generate_csrf,
            "DEFAULT_PRIORITIES": DEFAULT_PRIORITIES,
            "utc_naive_to_jalali_str": utc_naive_to_jalali_str,
            "get_task_status": get_task_status_python,
            "localize_digits": localize_digits,
            "static_version": static_version,
        }

    @app.context_processor
    def inject_user_prefs():
        """Inject user language, date_format, translation dict, and localized
        default priorities into every template."""
        if current_user.is_authenticated:
            lang = current_user.language
            date_fmt = current_user.date_format
            date_style = current_user.date_display_style
        else:
            lang = session.get('anon_lang', 'fa')
            date_fmt = 'jalali'
            date_style = 'text'

        t = get_translations(lang)
        loc_priorities = get_localized_priorities(lang)  # list of (storage_key, display)

        return dict(
            user_lang=lang,
            user_date_fmt=date_fmt,
            user_date_style=date_style,
            t=t,
            localized_default_priorities=loc_priorities,
        )

    # ---------------------------------------------------------------------
    # ⬛ AUTH ROUTES: User registration, login, logout, and language switching
    # ---------------------------------------------------------------------

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """
        GET  /register — render registration form.
        POST /register — validate, create user, redirect to login.
        """
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = RegisterForm()
        if form.validate_on_submit():

            if not PASSWORD_REGEX.match(form.password.data):
                form.password.errors.append("val_password_format")
                return render_template("register.html", form=form)
            w1 = form.recovery_word_1.data.strip().lower()
            w2 = form.recovery_word_2.data.strip().lower()
            if w1 == w2:
                form.recovery_word_2.errors.append("val_rec_word_duplicate")
                return render_template("register.html", form=form)
            
            # Check duplicate username (case-insensitive)

            existing = User.query.filter(
                User.username.ilike(form.username.data.strip())
            ).first()
            if existing:
                form.username.errors.append("val_username_taken")
                return render_template("register.html", form=form)

            try:
                password_hash = bcrypt.generate_password_hash(
                    form.password.data
                ).decode("utf-8")
                
                w1_hash = bcrypt.generate_password_hash(form.recovery_word_1.data.strip().lower()).decode("utf-8")
                w2_hash = bcrypt.generate_password_hash(form.recovery_word_2.data.strip().lower()).decode("utf-8")

                user = User(
                    username=form.username.data.strip(),
                    name=form.name.data.strip(),
                    family=form.family.data.strip(),
                    password_hash=password_hash,
                    recovery_w1_hash=w1_hash,
                    recovery_w2_hash=w2_hash,
                )
                db.session.add(user)
                db.session.commit()
                flash(_t("flash_register_success"), "success")
                return redirect(url_for("login"))
            except ValueError as e:
                db.session.rollback()
                flash(_t(str(e)), "danger")
            except Exception:
                db.session.rollback()
                flash(_t("flash_error_generic"), "danger")

        return render_template("register.html", form=form)
    
    # ---------------------------------------------------------------------
    # ⬛ RECOVERY ROUTES: Password recovery via security word verification
    # ---------------------------------------------------------------------

    @app.route("/api/recovery/check", methods=["POST"])
    def recovery_check():
        username = request.json.get("username", "").strip()
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({"error": _t("recovery_err_user_not_found")}), 404
            
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.last_recovery_attempt:
            delta = now - user.last_recovery_attempt
            if delta.total_seconds() < 86400 and user.recovery_attempts >= 3:
                return jsonify({"error": _t("recovery_err_locked")}), 429
            elif delta.total_seconds() >= 86400:
                user.recovery_attempts = 0
                db.session.commit()

        return jsonify({"message": "OK"}), 200

    @app.route("/api/recovery/verify", methods=["POST"])
    def recovery_verify():
        data = request.json
        username = data.get("username", "").strip()
        guesses = data.get("guesses", [])
        
        user = User.query.filter_by(username=username).first()
        if not user or len(guesses) != 2:
            return jsonify({"error": _t("recovery_err_invalid_req")}), 400

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.last_recovery_attempt and (now - user.last_recovery_attempt).total_seconds() < 86400 and user.recovery_attempts >= 3:
            return jsonify({"error": _t("recovery_err_locked")}), 429

        normalized_guesses = [g.strip().lower() for g in guesses]
        
        match_1 = bcrypt.check_password_hash(user.recovery_w1_hash, normalized_guesses[0])
        match_2 = bcrypt.check_password_hash(user.recovery_w2_hash, normalized_guesses[1])

        if match_1 and match_2:
            session['recovery_user_id'] = user.id
            user.recovery_attempts = 0 
            db.session.commit()
            return jsonify({"message": _t("recovery_msg_ok")}), 200
        else:
            user.recovery_attempts += 1
            user.last_recovery_attempt = now
            db.session.commit()
            return jsonify({"error": _t("recovery_err_mismatch", n=3 - user.recovery_attempts)}), 401

    @app.route("/api/recovery/reset", methods=["POST"])
    def recovery_reset():
        if 'recovery_user_id' not in session:
            return jsonify({"error": _t("recovery_err_unauthorized")}), 403
            
        new_password = request.json.get("password", "")
        if len(new_password) < 8:
            return jsonify({"error": _t("recovery_err_min_length")}), 400
        
        if not PASSWORD_REGEX.match(new_password):
            return jsonify({"error": _t("val_password_format")}), 400
            
        user = User.query.get(session['recovery_user_id'])
        if user:
            user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
            db.session.commit()
            session.pop('recovery_user_id', None)
            return jsonify({"message": _t("recovery_msg_pass_changed")}), 200
            
        return jsonify({"error": _t("recovery_err_sys")}), 500

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        GET  /login — render login form.
        POST /login — validate credentials, start session, redirect to index.
        """
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.strip()).first()
            # Use same error message for wrong username OR wrong password (security)
            if not user or not bcrypt.check_password_hash(
                user.password_hash, form.password.data
            ):
                flash(_t("flash_login_bad_creds"), "danger")
                return render_template("login.html", form=form)

            login_user(user, remember=False)

            if user.recovery_attempts > 0:
                user.recovery_attempts = 0
                user.last_recovery_attempt = None
                db.session.commit()

            # If the visitor had chosen a language on the login/register pages,
            # apply it to their profile so the app immediately uses that language.
            anon_lang = session.pop('anon_lang', None)
            if anon_lang in ('fa', 'en') and anon_lang != user.language:
                user.language = anon_lang
                db.session.commit()

            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        return render_template("login.html", form=form)

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        """POST /logout — clear session, redirect to login. CSRF protected."""
        # Carry the user's language over to the anonymous session so login/register
        # pages stay in the same language after logout.
        if current_user.is_authenticated:
            session['anon_lang'] = current_user.language
        logout_user()
        flash(_t("flash_logout_success"), "info")
        return redirect(url_for("login"))

    @app.route("/set-lang/<lang>")
    def set_lang(lang: str):
        """
        GET /set-lang/<lang> — Toggle language for unauthenticated visitors.
        Authenticated users update their profile via /settings instead.
        Redirects back to the referring page (or /login as fallback).
        """
        if lang in ("fa", "en"):
            if current_user.is_authenticated:
                # Persist to DB profile
                current_user.language = lang
                db.session.commit()
            else:
                session['anon_lang'] = lang
        return redirect(request.referrer or url_for("login"))

    # ---------------------------------------------------------------------
    # ⬛ PUBLIC ROUTES: Landing page and authenticated dashboard
    # ---------------------------------------------------------------------

    @app.route("/")
    def landing():
        """
        GET / — Public landing page for anonymous visitors.
        Authenticated users are immediately redirected to their dashboard,
        matching the same convention applied on /login and /register.
        """
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        return render_template("landing.html")

    @app.route("/dashboard")
    @login_required
    def index():
        """
        GET /dashboard — fetch tasks with optional filters, compute status, render index.

        Query parameters:
            status    : 'all' | 'pending' | 'done' | 'expired'
            time_range: 'all' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom'
            priority  : priority string or 'all'
            start_date: Jalali string (only if time_range='custom')
            end_date  : Jalali string (only if time_range='custom')
        """
        status_filter = request.args.get("status", "all")
        time_range = request.args.get("time_range", "all")
        priority_filter = request.args.get("priority", "all")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")

        now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)

        # Build base query for current user
        query = Task.query.filter_by(user_id=current_user.id)

        # -- Status filter ---------------------------------------------------
        if status_filter == "pending":
            query = query.filter(
                and_(Task.is_done == False, Task.expires_at >= now_utc_naive)
            )
        elif status_filter == "done":
            query = query.filter(Task.is_done == True)
        elif status_filter == "expired":
            query = query.filter(
                and_(Task.is_done == False, Task.expires_at < now_utc_naive)
            )
        # else: 'all' — no status filter

        # -- Time range filter (applied on expires_at) ------------------------
        time_filter_error = None
        if time_range != "all":
            try:
                if time_range == "daily":
                    start_utc, end_utc = get_daily_range_utc()
                elif time_range == "weekly":
                    start_utc, end_utc = get_weekly_range_utc()
                elif time_range == "monthly":
                    start_utc, end_utc = get_monthly_range_utc()
                elif time_range == "yearly":
                    start_utc, end_utc = get_yearly_range_utc()
                elif time_range == "custom":
                    if not start_date or not end_date:
                        # Validation failure: reset query to base, skip all filters
                        time_filter_error = _t("val_date_range_both_required")
                        query = Task.query.filter_by(user_id=current_user.id)
                    else:
                        start_utc, end_utc = get_custom_range_utc(start_date, end_date)
                else:
                    start_utc, end_utc = None, None

                if not time_filter_error and time_range in (
                    "daily", "weekly", "monthly", "yearly", "custom"
                ):
                    query = query.filter(
                        and_(
                            Task.expires_at >= start_utc,
                            Task.expires_at <= end_utc,
                        )
                    )
            except ValueError as e:
                time_filter_error = _t(str(e))

        # -- Priority filter (skipped when time_filter_error blocks the request) --
        if not time_filter_error and priority_filter and priority_filter != "all":
            query = query.filter(Task.priority == priority_filter)

        # -- Ordering: pending → done → expired (server-side via CASE) -------
        status_order = case(
            (and_(Task.is_done == False, Task.expires_at >= now_utc_naive), 0),
            (Task.is_done == True, 1),
            (and_(Task.is_done == False, Task.expires_at < now_utc_naive), 2),
            else_=3,
        )
        tasks = query.order_by(status_order, Task.expires_at.asc()).all()

        # Attach computed status to each task for template use
        for task in tasks:
            task.status = get_task_status_python(task.is_done, task.expires_at)

        # Get user's custom priorities for filter/create dropdowns
        user_custom_priorities = CustomPriority.query.filter_by(
            user_id=current_user.id
        ).all()
        all_priorities = DEFAULT_PRIORITIES + [cp.name for cp in user_custom_priorities]

        # Forms for modals
        task_form = TaskForm()
        edit_form = EditTaskForm()
        csrf_form = CSRFForm()

        return render_template(
            "index.html",
            tasks=tasks,
            task_form=task_form,
            edit_form=edit_form,
            csrf_form=csrf_form,
            all_priorities=all_priorities,
            status_filter=status_filter,
            time_range=time_range,
            priority_filter=priority_filter,
            start_date=start_date,
            end_date=end_date,
            time_filter_error=time_filter_error,
            now_utc_naive=now_utc_naive,
        )

    # ---------------------------------------------------------------------
    # ⬛ TASK CRUD ROUTES: Create, edit, mark-done, and delete tasks
    # ---------------------------------------------------------------------

    @app.route("/tasks/create", methods=["POST"])
    @login_required
    def task_create():
        """POST /tasks/create — validate form, convert Jalali→UTC, save task."""
        form = TaskForm()
        if form.validate_on_submit():
            try:
                expires_at_utc = jalali_str_to_utc_naive(form.expires_at.data)
            except ValueError as e:
                flash(_t(str(e)), "danger")
                return redirect(url_for("index"))

            try:
                task = Task(
                    user_id=current_user.id,
                    title=form.title.data.strip(),
                    description=form.description.data.strip() if form.description.data else None,
                    priority=form.priority.data.strip() if form.priority.data else None,
                    expires_at=expires_at_utc,
                    estimated_time=form.estimated_time.data,
                )
                db.session.add(task)
                db.session.commit()
                flash(_t("flash_task_created"), "success")
            except ValueError as e:
                db.session.rollback()
                flash(_t(str(e)), "danger")
            except Exception:
                db.session.rollback()
                flash(_t("flash_error_generic"), "danger")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    flash(_t(error), "danger")

        return redirect(url_for("index"))

    @app.route("/tasks/<int:task_id>/edit", methods=["POST"])
    @login_required
    def task_edit(task_id: int):
        """
        POST /tasks/<id>/edit — edit a pending task (priority, expires_at, estimated_time).

        Ownership is asserted. Only pending tasks can be edited.
        title and description are NOT updated (they are readonly in the edit modal).
        """
        task = Task.query.get_or_404(task_id)

        # Ownership check
        if task.user_id != current_user.id:
            abort(403)

        # Only pending tasks can be edited
        status = get_task_status_python(task.is_done, task.expires_at)
        if status != "pending":
            flash(_t("flash_only_pending_edit"), "warning")
            return redirect(url_for("index"))

        form = EditTaskForm()
        if form.validate_on_submit():
            try:
                expires_at_utc = jalali_str_to_utc_naive(form.expires_at.data)
            except ValueError as e:
                flash(_t(str(e)), "danger")
                return redirect(url_for("index"))

            try:
                task.priority = form.priority.data.strip() if form.priority.data else None
                task.expires_at = expires_at_utc
                task.estimated_time = form.estimated_time.data
                db.session.commit()
                flash(_t("flash_task_edited"), "success")
            except ValueError as e:
                db.session.rollback()
                flash(_t(str(e)), "danger")
            except Exception:
                db.session.rollback()
                flash(_t("flash_error_generic"), "danger")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    flash(_t(error), "danger")

        return redirect(url_for("index"))

    @app.route("/tasks/<int:task_id>/done", methods=["POST"])
    @login_required
    def task_done(task_id: int):
        """POST /tasks/<id>/done — mark task as done. Ownership asserted."""
        task = Task.query.get_or_404(task_id)

        if task.user_id != current_user.id:
            abort(403)

        status = get_task_status_python(task.is_done, task.expires_at)
        if status != "pending":
            flash(_t("flash_only_pending_done"), "warning")
            return redirect(url_for("index"))

        try:
            task.is_done = True
            db.session.commit()
            flash(_t("flash_task_done"), "success")
        except Exception:
            db.session.rollback()
            flash(_t("flash_error_short"), "danger")

        return redirect(url_for("index"))

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    @login_required
    def task_delete(task_id: int):
        """POST /tasks/<id>/delete — hard delete a task. Ownership asserted."""
        task = Task.query.get_or_404(task_id)

        if task.user_id != current_user.id:
            abort(403)

        try:
            db.session.delete(task)
            db.session.commit()
            flash(_t("flash_task_deleted"), "success")
        except Exception:
            db.session.rollback()
            flash(_t("flash_error_short"), "danger")

        return redirect(url_for("index"))

    # ---------------------------------------------------------------------
    # ⬛ CUSTOM PRIORITY ROUTES: User-defined priority label management
    # ---------------------------------------------------------------------

    @app.route("/priorities")
    @login_required
    def priorities_list():
        """GET /priorities — return user's custom priorities as JSON."""
        priorities = CustomPriority.query.filter_by(user_id=current_user.id).all()
        return jsonify(
            [{"id": p.id, "name": p.name} for p in priorities]
        )

    @app.route("/priorities/create", methods=["POST"])
    @login_required
    def priority_create():
        """
        POST /priorities/create — create a custom priority.

        Validates:
            - name length (2–15)
            - name not duplicate of defaults or existing user priorities
            - max 3 custom priorities per user
        """
        form = CustomPriorityForm()
        # Determine where to redirect after action
        next_url = request.form.get("next_url", url_for("settings"))

        if form.validate_on_submit():
            name = form.name.data.strip()

            # Max 3 per user
            existing_count = CustomPriority.query.filter_by(
                user_id=current_user.id
            ).count()
            if existing_count >= 5:
                flash(_t("flash_priority_max"), "danger")
                return redirect(next_url)

            # Uniqueness against defaults and user's existing
            if name in DEFAULT_PRIORITIES:
                flash(_t("flash_priority_is_default", name=name), "danger")
                return redirect(next_url)

            existing_custom = CustomPriority.query.filter_by(
                user_id=current_user.id, name=name
            ).first()
            if existing_custom:
                flash(_t("flash_priority_duplicate", name=name), "danger")
                return redirect(next_url)

            try:
                priority = CustomPriority(user_id=current_user.id, name=name)
                db.session.add(priority)
                db.session.commit()
                flash(_t("flash_priority_created", name=name), "success")
            except ValueError as e:
                db.session.rollback()
                flash(_t(str(e)), "danger")
            except Exception:
                db.session.rollback()
                flash(_t("flash_error_short"), "danger")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    flash(_t(error), "danger")

        return redirect(next_url)

    @app.route("/priorities/<int:priority_id>/delete", methods=["POST"])
    @login_required
    def priority_delete(priority_id: int):
        """
        POST /priorities/<id>/delete — delete a custom priority.

        Checks that no pending tasks use this priority before deletion.
        If tasks do use it, NULL out the priority field on those tasks, then delete.
        """
        priority = CustomPriority.query.get_or_404(priority_id)

        if priority.user_id != current_user.id:
            abort(403)

        next_url = request.form.get("next_url", url_for("settings"))

        try:
            # NULL out the priority on all user tasks that reference this priority
            affected_tasks = Task.query.filter_by(
                user_id=current_user.id,
                priority=priority.name,
            ).all()
            for t in affected_tasks:
                t.priority = None

            db.session.delete(priority)
            db.session.commit()
            flash(_t("flash_priority_deleted", name=priority.name), "success")
        except Exception:
            db.session.rollback()
            flash(_t("flash_error_short"), "danger")

        return redirect(next_url)

    # ---------------------------------------------------------------------
    # ⬛ SETTINGS ROUTE: User preferences for language and date format
    # ---------------------------------------------------------------------

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        """
        GET  /settings — render settings page (language, date format, priorities).
        POST /settings — save language/date_format preferences.
        """
        settings_form = SettingsForm(
            language=current_user.language,
            date_format=current_user.date_format,
            date_display_style=current_user.date_display_style,
        )
        priority_form = CustomPriorityForm()
        csrf_form = CSRFForm()

        if settings_form.validate_on_submit():
            try:
                current_user.language = settings_form.language.data
                current_user.date_format = settings_form.date_format.data
                current_user.date_display_style = settings_form.date_display_style.data
                db.session.commit()
                # Use the NEW language the user just saved for the flash message
                new_lang = settings_form.language.data
                saved_msg = get_translations(new_lang).get("flash_settings_saved", "Settings saved.")
                flash(saved_msg, "success")
            except ValueError as e:
                db.session.rollback()
                flash(_t(str(e)), "danger")
            except Exception:
                db.session.rollback()
                flash(_t("flash_error_short"), "danger")
            return redirect(url_for("settings"))

        user_custom_priorities = CustomPriority.query.filter_by(
            user_id=current_user.id
        ).all()

        return render_template(
            "settings.html",
            settings_form=settings_form,
            priority_form=priority_form,
            csrf_form=csrf_form,
            custom_priorities=user_custom_priorities,
        )

    # ---------------------------------------------------------------------
    # ⬛ ANALYTICS ROUTE: Task statistics with filtered donut charts
    # ---------------------------------------------------------------------

    @app.route("/analytics")
    @login_required
    def analytics():
        """
        GET /analytics — analytics page with two donut charts.

        Box 1: Total counts across all user tasks.
        Box 2: Filtered counts based on GET params (same filter options as index).
        """
        now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)

        def _compute_counts(base_query):
            """Return dict with pending, done, expired counts."""
            all_tasks = base_query.all()
            counts = {"pending": 0, "done": 0, "expired": 0}
            for task in all_tasks:
                s = get_task_status_python(task.is_done, task.expires_at)
                counts[s] += 1
            return counts

        # Box 1: all tasks
        all_tasks_query = Task.query.filter_by(user_id=current_user.id)
        box1_counts = _compute_counts(all_tasks_query)
        box1_total = sum(box1_counts.values())

        # Box 2: filtered tasks
        time_range = request.args.get("time_range", "all")
        priority_filter = request.args.get("priority", "all")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")

        filtered_query = Task.query.filter_by(user_id=current_user.id)
        time_filter_error = None

        if time_range != "all":
            try:
                if time_range == "daily":
                    start_utc, end_utc = get_daily_range_utc()
                elif time_range == "weekly":
                    start_utc, end_utc = get_weekly_range_utc()
                elif time_range == "monthly":
                    start_utc, end_utc = get_monthly_range_utc()
                elif time_range == "yearly":
                    start_utc, end_utc = get_yearly_range_utc()
                elif time_range == "custom":
                    if not start_date or not end_date:
                        # Validation failure: reset filtered_query to base, skip all filters
                        time_filter_error = _t("val_date_range_both_required")
                        filtered_query = Task.query.filter_by(user_id=current_user.id)
                    else:
                        start_utc, end_utc = get_custom_range_utc(start_date, end_date)
                else:
                    start_utc, end_utc = None, None

                if not time_filter_error and time_range in (
                    "daily", "weekly", "monthly", "yearly", "custom"
                ):
                    filtered_query = filtered_query.filter(
                        and_(
                            Task.expires_at >= start_utc,
                            Task.expires_at <= end_utc,
                        )
                    )
            except ValueError as e:
                time_filter_error = _t(str(e))

        # Priority filter (skipped when time_filter_error blocks the request)
        if not time_filter_error and priority_filter and priority_filter != "all":
            filtered_query = filtered_query.filter(Task.priority == priority_filter)

        box2_counts = _compute_counts(filtered_query)
        box2_total = sum(box2_counts.values())

        # Custom priorities for filter dropdown
        user_custom_priorities = CustomPriority.query.filter_by(
            user_id=current_user.id
        ).all()
        all_priorities = DEFAULT_PRIORITIES + [cp.name for cp in user_custom_priorities]

        csrf_form = CSRFForm()

        return render_template(
            "analytics.html",
            box1_counts=box1_counts,
            box1_total=box1_total,
            box2_counts=box2_counts,
            box2_total=box2_total,
            all_priorities=all_priorities,
            time_range=time_range,
            priority_filter=priority_filter,
            start_date=start_date,
            end_date=end_date,
            time_filter_error=time_filter_error,
            csrf_form=csrf_form,
        )
    

    # ---------------------------------------------------------------------
    # ⬛ PWA ROUTES: Service Worker and manifest serving
    # ---------------------------------------------------------------------
    
    @app.route("/sw.js")
    def service_worker():
        """Serve the Service Worker from the root scope."""
        response = app.send_static_file("sw.js")
        response.headers['Cache-Control'] = 'no-cache'
        return response

    @app.route("/manifest.json")
    def manifest():
        """Serve the PWA manifest file."""
        return app.send_static_file("manifest.json")
    

    # ---------------------------------------------------------------------
    # ⬛ DATABASE INITIALIZATION: CLI command for table creation
    # ---------------------------------------------------------------------

    @app.cli.command("init-db")
    def init_db_command():
        """Create all database tables."""
        db.create_all()
        print("پایگاه داده با موفقیت ساخته شد.")

    return app


# ---------------------------------------------------------------------
# ⬛ ENTRY POINT: App instantiation and development server
# ---------------------------------------------------------------------

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG", "0") == "1")