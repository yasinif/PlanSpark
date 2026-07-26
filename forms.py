"""
forms.py — Flask-WTF form definitions for the Persian To-Do List app.

All forms include CSRF protection via FlaskForm (enabled by WTF_CSRF_ENABLED).
Validation mirrors the @validates rules in models.py (dual-layer enforcement).

Delta: Added SettingsForm for language/date_format preferences.
Note: All validator message= values are translation keys (val_*) resolved
      at flash time via get_translations() in app.py.
"""

# =====================================================================
# FILE: forms.py
# PURPOSE: Defines all WTForms form classes for the TaskMen application, covering user authentication, task management, settings, and custom priorities.
# =====================================================================

import re

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,
)

# ---------------------------------------------------------------------
# ⬛ SHARED VALIDATOR CONSTANTS: Regex patterns and text normalization
# ---------------------------------------------------------------------

# Name fields: accept Persian script, Latin letters (A-Z/a-z), and spaces.
# Explicitly rejects: ASCII digits (0-9), Persian digits (۰-۹), symbols, punctuation.
NAME_PATTERN = r"^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200c A-Za-z]+$"

# Username: strict ASCII alphanumeric only.
# Explicitly rejects: Persian/Unicode letters, underscores, spaces, symbols.
USERNAME_PATTERN = r"^[A-Za-z0-9]+$"
# Security Words: ONLY Persian and English letters. NO spaces, NO digits, NO symbols.
WORD_PATTERN = r"^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200cA-Za-z]+$"

def normalize_text(value):
    """Normalize line endings (\\r\\n -> \\n) and strip whitespace to match JS length."""
    if value:
        return value.replace('\r\n', '\n').strip()
    return value


# ---------------------------------------------------------------------
# ⬛ REGISTRATION FORM: New user sign-up with recovery words
# ---------------------------------------------------------------------

class RegisterForm(FlaskForm):
    """Form for new user registration."""

    username = StringField(
        "نام کاربری",
        validators=[
            DataRequired(message="val_username_required"),
            Length(min=5, max=20, message="val_username_length"),
            Regexp(
                USERNAME_PATTERN,
                message="val_username_format",
            ),
        ],
    )
    name = StringField(
        "نام",
        validators=[
            DataRequired(message="val_name_required"),
            Length(min=2, max=30, message="val_name_length"),
            Regexp(
                NAME_PATTERN,
                message="val_name_letters_only",
            ),
        ],
    )
    family = StringField(
        "نام خانوادگی",
        validators=[
            DataRequired(message="val_family_required"),
            Length(min=2, max=30, message="val_family_length"),
            Regexp(
                NAME_PATTERN,
                message="val_family_letters_only",
            ),
        ],
    )

    recovery_word_1 = StringField(
        "کلمه امنیتی اول",
        validators=[
            DataRequired(message="val_rec_word_required"),
            Length(min=5, max=30, message="val_rec_word_length"),
            Regexp(WORD_PATTERN, message="val_rec_word_format"),
        ],
    )
    recovery_word_2 = StringField(
        "کلمه امنیتی دوم",
        validators=[
            DataRequired(message="val_rec_word_required"),
            Length(min=5, max=30, message="val_rec_word_length"),
            Regexp(WORD_PATTERN, message="val_rec_word_format"),
        ],
    )

    password = PasswordField(
        "رمز عبور",
        validators=[
            DataRequired(message="val_password_required"),
            Length(min=8, message="val_password_length"),
        ],
    )
    confirm_password = PasswordField(
        "تکرار رمز عبور",
        validators=[
            DataRequired(message="val_confirm_required"),
            EqualTo("password", message="val_confirm_mismatch"),
        ],
    )


# ---------------------------------------------------------------------
# ⬛ LOGIN FORM: Username and password authentication
# ---------------------------------------------------------------------

class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField(
        "نام کاربری",
        validators=[
            DataRequired(message="val_username_required"),
        ],
    )
    password = PasswordField(
        "رمز عبور",
        validators=[
            DataRequired(message="val_password_required"),
        ],
    )


# ---------------------------------------------------------------------
# ⬛ TASK CREATION FORM: New task with Jalali date and priority
# ---------------------------------------------------------------------

class TaskForm(FlaskForm):
    """Form for creating a new task."""

    title = StringField(
        "عنوان",
        filters=[normalize_text],
        validators=[
            DataRequired(message="val_title_required"),
            Length(max=100, message="val_title_length"),
        ],
    )
    description = TextAreaField(
        "توضیحات",
        filters=[normalize_text],
        validators=[
            Optional(),
            Length(max=500, message="val_description_length"),
        ],
    )
    priority = StringField(
        "اولویت",
        validators=[Optional()],
    )
    # Delta 2.5: expires_at is now assembled from two hidden fields by JS
    # (expires_date_hidden + expires_time_hidden → combined → this field)
    expires_at = StringField(
        "تاریخ انقضا (شمسی)",
        validators=[
            DataRequired(message="val_expires_required"),
        ],
    )
    estimated_time = IntegerField(
        "زمان تخمینی (دقیقه)",
        validators=[
            Optional(),
            NumberRange(min=0, message="val_estimated_negative"),
        ],
    )


# ---------------------------------------------------------------------
# ⬛ TASK EDIT FORM: Modify pending task priority, deadline, and estimate
# ---------------------------------------------------------------------

class EditTaskForm(FlaskForm):
    """
    Form for editing a pending task.
    title and description are shown as readonly; only priority, expires_at,
    and estimated_time are editable.
    """

    # Read-only display fields (submitted but not applied to model)
    title = StringField(
        "عنوان",
        filters=[normalize_text],
        validators=[
            Optional(),
            Length(max=100),
        ],
    )
    description = TextAreaField(
        "توضیحات",
        filters=[normalize_text],
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    # Editable fields
    priority = StringField(
        "اولویت",
        validators=[Optional()],
    )
    # Delta 2.5: same split-picker pattern as TaskForm
    expires_at = StringField(
        "تاریخ انقضا (شمسی)",
        validators=[
            DataRequired(message="val_expires_required"),
        ],
    )
    estimated_time = IntegerField(
        "زمان تخمینی (دقیقه)",
        validators=[
            Optional(),
            NumberRange(min=0, message="val_estimated_negative"),
        ],
    )


# ---------------------------------------------------------------------
# ⬛ CUSTOM PRIORITY FORM: User-defined priority label creation
# ---------------------------------------------------------------------

class CustomPriorityForm(FlaskForm):
    """Form for creating a custom priority label."""

    name = StringField(
        "نام اولویت",
        validators=[
            DataRequired(message="val_priority_name_required"),
            Length(min=2, max=15, message="val_priority_name_length"),
        ],
    )


# ---------------------------------------------------------------------
# ⬛ SETTINGS FORM: Language and date format preferences
# ---------------------------------------------------------------------

class SettingsForm(FlaskForm):
    """Form for user language and date-format preferences."""

    language = RadioField(
        "زبان",
        choices=[("fa", "فارسی"), ("en", "English")],
        validators=[DataRequired(message="val_settings_lang_required")],
    )
    date_format = RadioField(
        "نوع تاریخ",
        choices=[("jalali", "شمسی (جلالی)"), ("gregorian", "میلادی")],
        validators=[DataRequired(message="val_settings_date_required")],
    )
    date_display_style = RadioField(
        "نوع نمایش تاریخ",
        choices=[("text", "ترکیبی"), ("numeric", "عددی")],
        validators=[DataRequired(message="val_settings_date_required")],
    )


# ---------------------------------------------------------------------
# ⬛ CSRF-ONLY FORM: Minimal CSRF token for action endpoints
# ---------------------------------------------------------------------

class CSRFForm(FlaskForm):
    """Minimal form used only to generate and validate CSRF tokens for action endpoints."""
    pass
