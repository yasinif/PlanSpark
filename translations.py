"""
translations.py — UI string translations for FA (Persian) and EN (English).

Usage in app.py context processor:
    from translations import get_translations
    t = get_translations(current_user.language)   # returns a dict

Usage in templates:
    {{ t.page_title_tasks }}
    {{ t.btn_save }}

Rules:
  - Keys are snake_case and language-neutral.
  - Every key MUST exist in both 'fa' and 'en' dicts.
  - Persian flash messages are kept in app.py (server-side); only UI strings live here.
  - DEFAULT_PRIORITIES translated here as priority_low/medium/high so the
    index/analytics dropdowns can render in the active language.
"""

# =====================================================================
# FILE: translations.py
# PURPOSE: Centralized bilingual translation dictionary providing all user-facing strings in Persian and English, consumed by the get_translation() helper.
# =====================================================================

# ---------------------------------------------------------------------
# ⬛ TRANSLATIONS DICTIONARY: Complete FA/EN string mappings for all UI surfaces
# ---------------------------------------------------------------------
TRANSLATIONS = {
    "fa": {
        # ── Brand / Global ───────────────────────────────────────────
        "brand":                     "پلن‌اسپارک",
        "app_subtitle":              "(فارسی)مدیریت وظایف با تقویم شمسی",
        "clock_loading":             "در حال بارگذاری...",

        # ── Header actions ───────────────────────────────────────────
        "btn_login":                 "ورود",
        "btn_register":              "ثبت‌نام",
        "btn_logout":                "خروج",
        "logout_confirm":            "آیا مطمئن هستید که می‌خواهید خارج شوید؟",
        "theme_toggle_label":        "تغییر تم روشن/تاریک",
        "lang_switch_to_en":         "EN",
        "lang_switch_to_fa":         "فا",

        # ── Bottom nav ───────────────────────────────────────────────
        "nav_home":                  "خانه",
        "nav_analytics":             "آنالیز",
        "nav_settings":              "تنظیمات",

        # ── Auth — Login ─────────────────────────────────────────────
        "login_title":               "ورود",
        "login_subtitle":            "مدیریت وظایف فارسی با تقویم شمسی",
        "login_btn":                 "ورود به حساب",
        "login_no_account":          "حساب کاربری ندارید؟",
        "login_signup_link":         "ثبت‌نام کنید",
        "login_username_placeholder":"نام کاربری خود را وارد کنید",
        "login_password_placeholder":"رمز عبور خود را وارد کنید",
        "login_form_aria":           "فرم ورود",

        # ── Auth — Register ──────────────────────────────────────────
        "register_title":            "ثبت‌نام",
        "register_subtitle":         "ایجاد حساب کاربری جدید",
        "register_btn":              "ایجاد حساب کاربری",
        "register_have_account":     "قبلاً ثبت‌نام کرده‌اید؟",
        "register_login_link":       "وارد شوید",
        "register_form_aria":        "فرم ثبت‌نام",
        "register_name_placeholder": "نام",
        "register_family_placeholder": "نام خانوادگی",
        "register_username_placeholder":"حداقل ۵ کاراکتر (حروف انگلیسی، عدد، _)",
        "register_password_placeholder":"حداقل ۸ کاراکتر (حروف انگلیسی، عدد، &!@#$%)",
        "register_confirm_placeholder":"رمز عبور را مجدداً وارد کنید",
        "toggle_password_label":     "نمایش/پنهان کردن رمز عبور",
        "toggle_confirm_label":      "نمایش/پنهان کردن تکرار رمز عبور",

        # ── Form field labels (overrides WTForms labels in templates) ─
        "field_username":            "نام کاربری",
        "field_name":                "نام",
        "field_family":              "نام خانوادگی",
        "field_password":            "رمز عبور",
        "field_confirm_password":    "تکرار رمز عبور",
        "field_title":               "عنوان",
        "field_description":         "توضیحات",
        "field_priority":            "اولویت",
        "field_estimated_time":      "زمان تخمینی (دقیقه)",
        "field_expires_at":          "تاریخ و ساعت انقضا",

        # ── Index — Filter bar ───────────────────────────────────────
        "filter_title":              "فیلتر وظایف",
        "filter_status":             "وضعیت",
        "filter_time_range":         "بازه زمانی",
        "filter_priority":           "اولویت",
        "filter_from":               "از تاریخ",
        "filter_to":                 "تا تاریخ",
        "filter_apply":              "اعمال",
        "filter_clear":              "پاک‌ کردن",
        "filter_clear_filters":      "پاک‌ کردن فیلترها",

        # ── Status options ───────────────────────────────────────────
        "status_all":                "همه",
        "status_pending":            "در انتظار",
        "status_done":               "انجام شده",
        "status_expired":            "منقضی",

        # ── Time range options ───────────────────────────────────────
        "range_all":                 "همه",
        "range_daily":               "امروز",
        "range_weekly":              "این هفته",
        "range_monthly":             "این ماه",
        "range_yearly":              "امسال",
        "range_custom":              "سفارشی",

        # ── Index — Task list ────────────────────────────────────────
        "tasks_heading":             "وظایف من",
        "search_placeholder":        "جستجوی وظایف...",
        "btn_new_task":              "تسک جدید",
        "empty_tasks":               "هیچ تسکی یافت نشد.",
        "unit_minutes":              "دقیقه",
        "label_created_at":          "ایجاد شده",
        "label_expires_at":          "انقضا",
        "label_estimated":           "زمان تخمینی",

        # ── Task action buttons ──────────────────────────────────────
        "btn_mark_done":             "انجام شد",
        "btn_edit":                  "ویرایش",
        "btn_delete":                "حذف",
        "btn_cancel":                "انصراف",
        "btn_save_task":             "ذخیره تسک",
        "btn_save_changes":          "ذخیره تغییرات",
        "delete_confirm":            "آیا مطمئن هستید که می‌خواهید این تسک را حذف کنید؟ این عمل قابل بازگشت نیست.",
        "done_badge":                " انجام شد",
        "expired_badge":             " منقضی",

        # ── Modals ───────────────────────────────────────────────────
        "modal_create_title":        "تسک جدید",
        "modal_edit_title":          "ویرایش تسک",
        "modal_edit_readonly_msg":   " عنوان و توضیحات قابل ویرایش نیستند و فقط برای مشاهده نمایش داده می‌شوند.",
        "field_title_readonly":      "عنوان (غیرقابل ویرایش)",
        "field_desc_readonly":       "توضیحات (غیرقابل ویرایش)",
        "no_priority":               "— بدون اولویت —",
        "placeholder_title":         "عنوان وظیفه",
        "placeholder_desc":          "توضیحات اختیاری...",
        "placeholder_minutes":       "مثال: ۳۰",

        # ── Date / Time picker ───────────────────────────────────────
        "picker_not_selected":       "— انتخاب نشده —",
        "picker_select_date":        "انتخاب تاریخ",
        "picker_select_time":        "انتخاب ساعت",
        "picker_confirm":            "تأیید",
        "picker_unit_hour":          "ساعت",
        "picker_unit_minute":        "دقیقه",
        "picker_hint":               "اگر ساعت انتخاب نشود، انتهای روز (۲۳:۵۹) محاسبه می‌شود.",
        "est_not_set":               "— تعیین نشده —",
        "est_select":                "تخمین زمان",
        "cal_prev_month":            "ماه قبل",
        "cal_next_month":            "ماه بعد",
        "cal_aria":                  "تقویم شمسی",
        "time_picker_aria":          "انتخاب ساعت",
        # Weekday column headers (Sat→Fri)
        "cal_headers":               ["ش", "ی", "د", "س", "چ", "پ", "ج"],

        # ── Analytics ────────────────────────────────────────────────
        "analytics_title":           "آمار و تحلیل وظایف",
        "analytics_overview":        "نمای کلی",
        "analytics_overview_sub":    "تمام وظایف شما",
        "analytics_filtered":        "آمار فیلتر شده",
        "analytics_filtered_sub":    "بر اساس بازه زمانی و اولویت",
        "analytics_total":           "مجموع:",
        "analytics_tasks_unit":      "تسک",
        "analytics_no_tasks":        "هیچ تسکی وجود ندارد",
        "analytics_no_tasks_range":  "هیچ تسکی در این بازه وجود ندارد",
        "analytics_back":            "← بازگشت به خانه",
        "chart_legend_aria":         "راهنمای نمودار",

        # ── Settings ─────────────────────────────────────────────────
        "settings_title":            "تنظیمات",
        "settings_theme_card":       "پوسته (تم) برنامه",
        "theme_light":               "حالت روشن",
        "theme_dark":                "حالت تاریک",
        "settings_lang_card":        " زبان و نوع تاریخ",
        "settings_lang_label":       "زبان نمایش",
        "lang_fa_name":              "فارسی",
        "lang_en_name":              "انگلیسی",
        "settings_date_label":       "نوع تاریخ",
        "date_jalali":               "شمسی",
        "date_gregorian":            "میلادی",
        "settings_date_style_label": "نوع نمایش تاریخ",
        "date_style_text":           "ماه‌متنی",
        "date_style_numeric":        "کاملاً‌عددی",
        "settings_save":             " ذخیره تنظیمات",
        "settings_priorities_card":  " اولویت‌های سفارشی",
        "settings_priorities_hint":  "حداکثر ۵ اولویت سفارشی می‌توانید تعریف کنید.",
        "settings_defaults_heading": "اولویت‌های پیش‌فرض",
        "settings_custom_heading":   "اولویت‌های سفارشی شما",
        "settings_no_custom":        "هنوز اولویت سفارشی تعریف نشده.",
        "settings_add_priority":     " اضافه کردن اولویت",
        "settings_add_limit":        " اضافه کردن اولویت (محدودیت ۵)",
        "settings_new_name_label":   "نام اولویت جدید",
        "settings_new_name_placeholder": "حداقل ۲، حداکثر ۱۵ کاراکتر",
        "settings_delete_priority_confirm": "آیا می‌خواهید اولویت «{name}» را حذف کنید؟",
        "priority_badge_default":    "پیش‌فرض",
        "btn_delete_priority":       " حذف",
        "btn_save":                  "ذخیره",

        # ── Default priorities (for dropdown/display) ────────────────
        "priority_low":              "کم",
        "priority_medium":           "متوسط",
        "priority_high":             "زیاد",

        # ── Flash / alert messages (server-side notifications) ───────
        "flash_register_success":     "ثبت‌نام با موفقیت انجام شد. لطفاً وارد شوید.",
        "flash_register_username_taken": "این نام کاربری قبلاً ثبت شده است.",
        "flash_login_bad_creds":      "نام کاربری یا رمز عبور اشتباه است.",
        "flash_login_required":        "برای دسترسی ابتدا ثبت‌نام کنید.",
        "flash_logout_success":       "با موفقیت خارج شدید.",
        "flash_task_created":         "تسک با موفقیت ایجاد شد.",
        "flash_task_edited":          "تسک با موفقیت ویرایش شد.",
        "flash_task_done":            "تسک با موفقیت انجام شد.",
        "flash_task_deleted":         "تسک با موفقیت حذف شد.",
        "flash_only_pending_edit":    "فقط تسک‌های در انتظار قابل ویرایش هستند.",
        "flash_only_pending_done":    "فقط تسک‌های در انتظار قابل تکمیل هستند.",
        "flash_priority_max":         "حداکثر ۵ اولویت سفارشی می‌توانید تعریف کنید.",
        "flash_priority_is_default":  "اولویت «{name}» از پیش وجود دارد.",
        "flash_priority_duplicate":   "اولویت «{name}» قبلاً تعریف شده است.",
        "flash_priority_created":     "اولویت «{name}» با موفقیت ایجاد شد.",
        "flash_priority_deleted":     "اولویت «{name}» با موفقیت حذف شد.",
        "flash_settings_saved":       "تنظیمات با موفقیت ذخیره شد.",
        "flash_error_generic":        "خطایی رخ داد. لطفاً دوباره تلاش کنید.",
        "flash_error_short":          "خطایی رخ داد.",
        # JS validation alerts
        "js_alert_select_date":       "لطفاً تاریخ انقضا را انتخاب کنید.",

        # ── Form / model validation messages ───────────────────────
        "val_username_required":      "نام کاربری الزامی است.",
        "val_username_length":        "نام کاربری باید بین ۵ تا ۲۰ کاراکتر باشد.",
        "val_username_format":        "نام کاربری فقط می‌تواند شامل حروف لاتین و اعداد باشد.",
        "val_name_required":          "نام الزامی است.",
        "val_name_length":            "نام باید بین ۲ تا ۳۰ کاراکتر باشد.",
        "val_name_persian":           "نام باید فارسی باشد.",
        "val_name_letters_only":      "نام فقط می‌تواند شامل حروف (فارسی یا لاتین) باشد.",
        "val_family_required":        "نام خانوادگی الزامی است.",
        "val_family_length":          "نام خانوادگی باید بین ۲ تا ۳۰ کاراکتر باشد.",
        "val_family_persian":         "نام خانوادگی باید فارسی باشد.",
        "val_family_letters_only":    "نام خانوادگی فقط می‌تواند شامل حروف (فارسی یا لاتین) باشد.",
        "val_password_required":      "رمز عبور الزامی است.",
        "val_password_length":        "رمز عبور باید حداقل ۸ کاراکتر باشد.",
        "val_password_format":        "رمز عبور فقط می‌تواند شامل حروف انگلیسی، اعداد و نمادهای &!@#$% باشد.",
        "val_confirm_required":       "تکرار رمز عبور الزامی است.",
        "val_confirm_mismatch":       "رمزهای عبور با یکدیگر مطابقت ندارند.",
        "val_title_required":         "عنوان تسک الزامی است.",
        "val_title_length":           "عنوان نمی‌تواند بیشتر از ۱۰۰ کاراکتر باشد.",
        "val_description_length":     "توضیحات نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.",
        "val_expires_required":       "تاریخ انقضا الزامی است.",
        "val_estimated_negative":     "زمان تخمینی نمی‌تواند منفی باشد.",
        "val_priority_name_required": "نام اولویت الزامی است.",
        "val_priority_name_length":   "نام اولویت باید بین ۲ تا ۱۵ کاراکتر باشد.",
        "val_settings_lang_required": "انتخاب زبان الزامی است.",
        "val_settings_date_required": "انتخاب نوع تاریخ الزامی است.",
        "val_username_taken":         "این نام کاربری قبلاً ثبت شده است.",
        "val_date_range_both_required":"تاریخ شروع و پایان برای بازه سفارشی الزامی است.",
        "val_date_start_invalid":     "تاریخ شروع نامعتبر است.",
        "val_date_start_after_end":   "تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.",
        # JS UI strings (injected via window.I18N)
        "js_am":                      "ق.ظ",
        "js_pm":                      "ب.ظ",
        "js_not_selected":            "— انتخاب نشده —",

        # ── Landing page ──────────────────────────────────────────────────────
        "landing_eyebrow":            "طراحی‌شده برای بهره‌وری شخصی",
        "landing_hero_title":         "مدیریت وظایف با تقویم شمسی، دوزبانه و بدون دردسر",
        "landing_hero_sub":           "پلن‌اسپارک یک ابزار جامع برای برنامه‌ریزی روزانه با پشتیبانی کامل از تقویم شمسی و کاربری دو زبانه فارسی وانگلیسی.",
        "landing_cta_start":          "شروع کنید",
        "landing_cta_features":       "ویژگی‌ها",
        "landing_trust_1":            "رایگان و متن باز",
        "landing_trust_2":            "دوزبانه فارسی و انگلیسی",
        "landing_trust_3":            "تقویم شمسی بومی",
        "landing_feat_eyebrow":       "ویژگی‌های اصلی",
        "landing_feat_heading":       "هر آنچه برای مدیریت وظایف روزانه نیاز دارید",
        "landing_f1_title":           "تقویم میلادی / شمسی",
        "landing_f1_desc":            "وظایف خود را با تاریخ‌های شمسی وارد کنید و بهترین زمان‌بندی را در تقویم بومی خود تجربه کنید.",
        "landing_f2_title":           " دوزبانه RTL/LTR",
        "landing_f2_desc":            "کاملاً بهینه‌سازی‌شده برای دو زبان فارسی و انگلیسی با تغییر جهت واقعی در لحظه.",
        "landing_f3_title":           "نشانگر وضعیت هوشمند",
        "landing_f3_desc":            "یک دایره‌ای با کد رنگی که فوراً نشان می‌دهد که چند روز برای هر کار باقی مانده است.",
        "landing_f4_title":           "آنالیز و فیلتر پیشرفته",
        "landing_f4_desc":            "آمار وظایف را بر اساس وضعیت، بازه زمانی و اولویت با نمودار دایره‌ای تعاملی مشاهده کنید.",
        "landing_f5_title":           "طبقه‌بندی اولویت سفارشی",
        "landing_f5_desc":            "اولویت‌های پیش‌فرض و دلخواه سفارشی برای سازماندهی بهتر با تکیه بر رویکرد کاری شما.",
        "landing_f6_title":           "احراز هویت امن و مطمئن",
        "landing_f6_desc":            "ورود ایمن مبتنی بر Flask-Login با حفاظت CSRF و رمزهای هش‌شده Bcrypt.",
        "landing_why_eyebrow":        "چرا پلن‌اسپارک؟",
        "landing_why_heading":        "امنیت و کیفیت، اولویت ماست",
        "landing_why_sub":            "بدون وعده‌های توخالی — فقط یک ابزار کارآمد واقعی که هر روز در کنارتان خواهد بود.",
        "landing_w1_title":           "تقویم بومی واقعی",
        "landing_w1_desc":            "تاریخ‌های شمسی کاملاً پشتیبانی می‌شوند — نه فقط نمایش بلکه در هسته زمانی و فیلترینگ نیز.",
        "landing_w2_title":           "دسترسی آزاد و متن باز",
        "landing_w2_desc":            "پلن‌اسپارک کد باز است. هرکسی می‌تواند آن را بررسی، فورک و بهبود دهد.",
        "landing_w3_title":           "بدون آدرس، بدون نگرانی",
        "landing_w3_desc":            "هیچ اطلاعات شخصی فروخته نمی‌شود. رمزها با Bcrypt هش‌شده و فرم‌ها با CSRF محافظت می‌شوند.",
        "landing_reviews_eyebrow":    "نظرات کاربران",
        "landing_reviews_heading":    "آنچه کاربران می‌گویند",
        "landing_reviews_placeholder":"نظرات کاربران به زودی در اینجا نمایش داده خواهد شد.",
        "landing_faq_eyebrow":        "سوالات متداول",
        "landing_faq_heading":        "پاسخ‌های سریع پیش از شروع",
        "landing_faq1_q":             "آیا پلن‌اسپارک رایگان است؟",
        "landing_faq1_a":             "بله! تمام امکانات اصلی بدون هیچ هزینه‌ای قابل استفاده هستند. فقط یک حساب بسازید و شروع کنید.",
        "landing_faq2_q":             "آیا تقویم شمسی به درستی کار می‌کند؟",
        "landing_faq2_a":             "بله. تمام تاریخ‌ها، فیلترها و نمایش مهلت واقعیاً بر اساس تقویم شمسی هستند.",
        "landing_faq3_q":             "آیا می‌توانم زبان را تغییر دهم؟",
        "landing_faq3_a":             "بله. از صفحه ورود، ثبت‌نام و تنظیمات می‌توانید بین فارسی و انگلیسی جابجا شوید.",
        "landing_cta2_heading":       "آماده‌اید برنامه‌ریزی کنید؟",
        "landing_cta2_sub":           "همین الان به‌صورت رایگان به پلن‌اسپارک بپیوندید.",
        "landing_cta2_btn":           "شروع رایگان",
        "landing_footer_copy":        "حقوق محفوظ © ۲۰۲۶ پلن‌اسپارک",
        "landing_footer_top":         "بازگشت به بالا",

        # ── Recovery System ──────────────────────────────────────────
        "recovery_forgot_pass":      "رمز عبور خود را فراموش کرده‌اید؟",
        "recovery_title":            "بازیابی حساب کاربری",
        "recovery_step2_msg":        "برای تایید هویت، ۲ کلمه امنیتی که در زمان ثبت‌نام انتخاب کردید را وارد کنید.",
        "recovery_btn_verify":       "بررسی و تایید",
        "recovery_btn_cancel":       "انصراف",
        "recovery_new_pass_label":   "رمز عبور جدید",
        "recovery_new_pass_placeholder": "حداقل ۸ کاراکتر (حروف انگلیسی، عدد، &!@#$%)",
        "recovery_btn_save":         "ذخیره رمز عبور",
        "recovery_err_empty_user":   "ابتدا نام کاربری خود را در فیلد بالا وارد کنید.",
        "recovery_err_fill_all":     "لطفاً هر ۲ کلمه را پر کنید.",
        "recovery_err_min_length":   "رمز عبور باید حداقل ۸ کاراکتر باشد.",
        "recovery_err_network":      "خطای شبکه. لطفاً اتصال خود را بررسی کنید.",
        "recovery_msg_redirect":     " در حال انتقال...",
        "recovery_err_user_not_found": "کاربری با این نام یافت نشد.",
        "recovery_err_locked":       "به دلیل ۳ تلاش ناموفق، این قابلیت تا ۲۴ ساعت قفل است.",
        "recovery_msg_ok":           "تایید هویت موفقیت‌آمیز بود.",
        "recovery_err_invalid_req":  "درخواست نامعتبر است.",
        "recovery_err_mismatch":     "کلمات وارد شده اشتباه است. شما {n} بار دیگر فرصت دارید.",
        "recovery_err_unauthorized": "شما مجوز این کار را ندارید.",
        "recovery_msg_pass_changed": "رمز عبور با موفقیت تغییر کرد.",
        "recovery_err_sys":          "خطای سیستمی رخ داده است.",
        "field_rec_word1":           "کلمه ۱ (مثال: نام فیلم)",
        "field_rec_word2":           "کلمه ۲ (مثال: نام شهر)",
        "register_rec_info":         "این ۲ کلمه را برای بازیابی حساب به خاطر بسپارید (حداقل ۵ کاراکتر، فقط حروف فارسی/انگلیسی):",
        "val_rec_word_required":     "وارد کردن کلمه امنیتی الزامی است.",
        "val_rec_word_length":       "کلمات فقط می‌توانند شامل حروف (بدون فاصله، عدد یا علامت) باشند.",
        "val_rec_word_format":       "کلمات فقط می‌توانند شامل حروف فارسی یا انگلیسی باشند.",
        "val_rec_word_duplicate":    "کلمات امنیتی نمی‌توانند تکراری باشند.",

    },

    "en": {
        # ── Brand / Global ───────────────────────────────────────────
        "brand":                     "PlanSpark",
        "app_subtitle":              "Task management with Jalali calendar",
        "clock_loading":             "Loading...",

        # ── Header actions ───────────────────────────────────────────
        "btn_login":                 "Login",
        "btn_register":              "Register",
        "btn_logout":                "Logout",
        "logout_confirm":            "Are you sure you want to log out?",
        "theme_toggle_label":        "Toggle light/dark theme",
        "lang_switch_to_en":         "EN",
        "lang_switch_to_fa":         "فا",

        # ── Bottom nav ───────────────────────────────────────────────
        "nav_home":                  "Home",
        "nav_analytics":             "Analytics",
        "nav_settings":              "Settings",

        # ── Auth — Login ─────────────────────────────────────────────
        "login_title":               "Sign In",
        "login_subtitle":            "Persian task management with Jalali calendar",
        "login_btn":                 "Sign In",
        "login_no_account":          "Don't have an account?",
        "login_signup_link":         "Sign up",
        "login_username_placeholder":"Enter your username",
        "login_password_placeholder":"Enter your password",
        "login_form_aria":           "Login form",

        # ── Auth — Register ──────────────────────────────────────────
        "register_title":            "Create Account",
        "register_subtitle":         "Create a new account",
        "register_btn":              "Create Account",
        "register_have_account":     "Already have an account?",
        "register_login_link":       "Sign in",
        "register_form_aria":        "Registration form",
        "register_name_placeholder": "First name",
        "register_family_placeholder":"Last name",
        "register_username_placeholder":"Min 5 chars, letters, numbers, underscore (_)",
        "register_password_placeholder":"Min 8 chars (letters, numbers, &!@#$%)",
        "register_confirm_placeholder":"Repeat your password",
        "toggle_password_label":     "Show/hide password",
        "toggle_confirm_label":      "Show/hide confirm password",

        # ── Form field labels ────────────────────────────────────────
        "field_username":            "Username",
        "field_name":                "First Name",
        "field_family":              "Last Name",
        "field_password":            "Password",
        "field_confirm_password":    "Confirm Password",
        "field_title":               "Title",
        "field_description":         "Description",
        "field_priority":            "Priority",
        "field_estimated_time":      "Estimated Time (minutes)",
        "field_expires_at":          "Expiry Date & Time",

        # ── Index — Filter bar ───────────────────────────────────────
        "filter_title":              "Task Filters",
        "filter_status":             "Status",
        "filter_time_range":         "Time Range",
        "filter_priority":           "Priority",
        "filter_from":               "From Date",
        "filter_to":                 "To Date",
        "filter_apply":              "Apply",
        "filter_clear":              "Clear",
        "filter_clear_filters":      "Clear Filters",

        # ── Status options ───────────────────────────────────────────
        "status_all":                "All",
        "status_pending":            "Pending",
        "status_done":               "Done",
        "status_expired":            "Expired",

        # ── Time range options ───────────────────────────────────────
        "range_all":                 "All",
        "range_daily":               "Today",
        "range_weekly":              "This Week",
        "range_monthly":             "This Month",
        "range_yearly":              "This Year",
        "range_custom":              "Custom",

        # ── Index — Task list ────────────────────────────────────────
        "tasks_heading":             "My Tasks",
        "search_placeholder":        "Search tasks...",
        "btn_new_task":              "New Task",
        "empty_tasks":               "No tasks found.",
        "unit_minutes":              "min",
        "label_created_at":          "Created",
        "label_expires_at":          "Expires",
        "label_estimated":           "Estimated",

        # ── Task action buttons ──────────────────────────────────────
        "btn_mark_done":             "Mark Done",
        "btn_edit":                  "Edit",
        "btn_delete":                "Delete",
        "btn_cancel":                "Cancel",
        "btn_save_task":             "Save Task",
        "btn_save_changes":          "Save Changes",
        "delete_confirm":            "Are you sure you want to delete this task? This cannot be undone.",
        "done_badge":                " Done",
        "expired_badge":             " Expired",

        # ── Modals ───────────────────────────────────────────────────
        "modal_create_title":        "New Task",
        "modal_edit_title":          "Edit Task",
        "modal_edit_readonly_msg":   " Title and description are read-only and cannot be edited.",
        "field_title_readonly":      "Title (read-only)",
        "field_desc_readonly":       "Description (read-only)",
        "no_priority":               "— No Priority —",
        "placeholder_title":         "Task title",
        "placeholder_desc":          "Optional description...",
        "placeholder_minutes":       "e.g. 30",

        # ── Date / Time picker ───────────────────────────────────────
        "picker_not_selected":       "— Not selected —",
        "picker_select_date":        "Select Date",
        "picker_select_time":        "Select Time",
        "picker_confirm":            "Confirm",
        "picker_unit_hour":          "Hour",
        "picker_unit_minute":        "Minute",
        "picker_hint":               "If no time is selected, end of day (23:59) will be used.",
        "est_not_set":               "— Not set —",
        "est_select":                "Estimated Time",
        "cal_prev_month":            "Previous month",
        "cal_next_month":            "Next month",
        "cal_aria":                  "Jalali calendar",
        "time_picker_aria":          "Select time",
        # Weekday headers stay in Persian (calendar is always Jalali)
        "cal_headers":               ["Sh", "Ye", "Do", "Se", "Ch", "Pa", "Jo"],

        # ── Analytics ────────────────────────────────────────────────
        "analytics_title":           "Task Analytics",
        "analytics_overview":        "Overview",
        "analytics_overview_sub":    "All your tasks",
        "analytics_filtered":        "Filtered Stats",
        "analytics_filtered_sub":    "By time range and priority",
        "analytics_total":           "Total:",
        "analytics_tasks_unit":      "tasks",
        "analytics_no_tasks":        "No tasks found",
        "analytics_no_tasks_range":  "No tasks in this range",
        "analytics_back":            "← Back to Home",
        "chart_legend_aria":         "Chart legend",

        # ── Settings ─────────────────────────────────────────────────
        "settings_title":            "Settings",
        "settings_theme_card":       "Application Theme",
        "theme_light":               "Light Mode",
        "theme_dark":                "Dark Mode",
        "settings_lang_card":        " Language & Date Format",
        "settings_lang_label":       "Display Language",
        "lang_fa_name":              "Persian",
        "lang_en_name":              "English",
        "settings_date_label":       "Date Format",
        "date_jalali":               "Shamsi",
        "date_gregorian":            "Gregorian",
        "settings_date_style_label": "Date Display Style",
        "date_style_text":           "Textual Month",
        "date_style_numeric":        "Fully Numeric",
        "settings_save":             " Save Settings",
        "settings_priorities_card":  " Custom Priorities",
        "settings_priorities_hint":  "You can define up to 5 custom priorities.",
        "settings_defaults_heading": "Default Priorities",
        "settings_custom_heading":   "Your Custom Priorities",
        "settings_no_custom":        "No custom priorities defined yet.",
        "settings_add_priority":     " Add Priority",
        "settings_add_limit":        " Add Priority (limit: 5)",
        "settings_new_name_label":   "New Priority Name",
        "settings_new_name_placeholder": "Min 2, max 15 characters",
        "settings_delete_priority_confirm": "Delete priority \"{name}\"?",
        "priority_badge_default":    "Default",
        "btn_delete_priority":       " Delete",
        "btn_save":                  "Save",

        # ── Default priorities (for dropdown/display) ────────────────
        "priority_low":              "Low",
        "priority_medium":           "Medium",
        "priority_high":             "High",

        # ── Flash / alert messages (server-side notifications) ───────
        "flash_register_success":     "Registration successful. Please log in.",
        "flash_register_username_taken": "This username is already taken.",
        "flash_login_bad_creds":      "Incorrect username or password.",
        "flash_login_required":        "Please sign up to continue.",
        "flash_logout_success":       "You have been logged out.",
        "flash_task_created":         "Task created successfully.",
        "flash_task_edited":          "Task updated successfully.",
        "flash_task_done":            "Task marked as done.",
        "flash_task_deleted":         "Task deleted successfully.",
        "flash_only_pending_edit":    "Only pending tasks can be edited.",
        "flash_only_pending_done":    "Only pending tasks can be marked as done.",
        "flash_priority_max":         "You can define a maximum of 5 custom priorities.",
        "flash_priority_is_default":  "Priority «{name}» already exists as a default.",
        "flash_priority_duplicate":   "Priority «{name}» is already defined.",
        "flash_priority_created":     "Priority «{name}» created successfully.",
        "flash_priority_deleted":     "Priority «{name}» deleted successfully.",
        "flash_settings_saved":       "Settings saved successfully.",
        "flash_error_generic":        "An error occurred. Please try again.",
        "flash_error_short":          "An error occurred.",
        # JS validation alerts
        "js_alert_select_date":       "Please select an expiry date.",

        # ── Form / model validation messages ───────────────────────
        "val_username_required":      "Username is required.",
        "val_username_length":        "Username must be between 5 and 20 characters.",
        "val_username_format":        "Username may only contain English letters and digits.",
        "val_name_required":          "First name is required.",
        "val_name_length":            "First name must be between 2 and 30 characters.",
        "val_name_persian":           "First name must be written in Persian.",
        "val_name_letters_only":      "First name may only contain letters (Persian or English).",
        "val_family_required":        "Last name is required.",
        "val_family_length":          "Last name must be between 2 and 30 characters.",
        "val_family_persian":         "Last name must be written in Persian.",
        "val_family_letters_only":    "Last name may only contain letters (Persian or English).",
        "val_password_required":      "Password is required.",
        "val_password_length":        "Password must be at least 8 characters.",
        "val_password_format":        "Password can only contain English letters, numbers, and &!@#$%.",
        "val_confirm_required":       "Please confirm your password.",
        "val_confirm_mismatch":       "Passwords do not match.",
        "val_title_required":         "Task title is required.",
        "val_title_length":           "Title cannot exceed 100 characters.",
        "val_description_length":     "Description cannot exceed 500 characters.",
        "val_expires_required":       "Expiry date is required.",
        "val_estimated_negative":     "Estimated time cannot be negative.",
        "val_priority_name_required": "Priority name is required.",
        "val_priority_name_length":   "Priority name must be between 2 and 15 characters.",
        "val_settings_lang_required": "Please select a language.",
        "val_settings_date_required": "Please select a date format.",
        "val_username_taken":         "This username is already registered.",
        "val_date_range_both_required":"Both start and end dates are required for a custom range.",
        "val_date_start_invalid":     "The start date is invalid.",
        "val_date_start_after_end":   "The start date cannot be after the end date.",
        # JS UI strings (injected via window.I18N)
        "js_am":                      "AM",
        "js_pm":                      "PM",
        "js_not_selected":            "— Not selected —",

        # ── Landing page ──────────────────────────────────────────────────────
        "landing_eyebrow":            "Built for personal productivity",
        "landing_hero_title":         "Task management with Shamsi calendar, bilingual and stress-free",
        "landing_hero_sub":           "PlanSpark is a complete tool for daily planning with full Gregorian/Shamsi calendar support and a bilingual Persian–English interface.",
        "landing_cta_start":          "Get Started",
        "landing_cta_features":       "Explore Features",
        "landing_trust_1":            "Free & Open Source",
        "landing_trust_2":            "Persian & English",
        "landing_trust_3":            "Native Shamsi Calendar",
        "landing_feat_eyebrow":       "Core Features",
        "landing_feat_heading":       "Everything you need for daily task management",
        "landing_f1_title":           "Gregorian / Shamsi Calendar",
        "landing_f1_desc":            "Enter tasks with Shamsi dates and experience the best scheduling in your native calendar.",
        "landing_f2_title":           "Bilingual RTL/LTR Interface",
        "landing_f2_desc":            "Fully optimised for both Persian and English with real-time direction switching.",
        "landing_f3_title":           "Smart Status Badge",
        "landing_f3_desc":            "A colour-coded circular badge instantly shows how many days remain for each task.",
        "landing_f4_title":           "Analytics & Advanced Filters",
        "landing_f4_desc":            "View task stats by status, time range and priority with an interactive donut chart.",
        "landing_f5_title":           "Custom Priority Levels",
        "landing_f5_desc":            "Default and custom priority labels to organise your workload your way.",
        "landing_f6_title":           "Secure Authentication",
        "landing_f6_desc":            "Flask-Login-based sign-in with CSRF protection and Bcrypt-hashed passwords.",
        "landing_why_eyebrow":        "Why PlanSpark?",
        "landing_why_heading":        "Security, quality and bilinguality — our priority",
        "landing_why_sub":            "No hollow promises — just a genuinely useful tool that will be by your side every day.",
        "landing_w1_title":           "Real Shamsi Calendar",
        "landing_w1_desc":            "Shamsi dates are fully supported — not just for display but also in range filtering.",
        "landing_w2_title":           "Free Access & Open Source",
        "landing_w2_desc":            "PlanSpark is open source. Anyone can inspect, fork and improve it.",
        "landing_w3_title":           "No Data Sold, No Worries",
        "landing_w3_desc":            "No personal data is sold. Passwords are Bcrypt-hashed and forms are CSRF-protected.",
        "landing_reviews_eyebrow":    "User Feedback",
        "landing_reviews_heading":    "What users are saying",
        "landing_reviews_placeholder":"User reviews will appear here soon.",
        "landing_faq_eyebrow":        "Frequently Asked Questions",
        "landing_faq_heading":        "Quick answers before you start",
        "landing_faq1_q":             "Is PlanSpark free?",
        "landing_faq1_a":             "Yes! All core features are available at no cost. Just register and start.",
        "landing_faq2_q":             "Does the Jalali calendar work correctly?",
        "landing_faq2_a":             "Yes. All dates, filters and deadline displays are genuinely Shamsi-based.",
        "landing_faq3_q":             "Can I switch language?",
        "landing_faq3_a":             "Yes. From the login, register or settings pages you can switch between Persian and English.",
        "landing_cta2_heading":       "Ready to plan smarter?",
        "landing_cta2_sub":           "Join PlanSpark for free, right now.",
        "landing_cta2_btn":           "Start for Free",
        "landing_footer_copy":        "All rights reserved © 2026 PlanSpark",
        "landing_footer_top":         "Back to top",

        # ── Recovery System ──────────────────────────────────────────
        "recovery_forgot_pass":      "Forgot your password?",
        "recovery_title":            "Account Recovery",
        "recovery_step2_msg":        "To verify your identity, enter the 2 security words you chose during registration.",
        "recovery_btn_verify":       "Verify",
        "recovery_btn_cancel":       "Cancel",
        "recovery_new_pass_label":   "New Password",
        "recovery_new_pass_placeholder": "Min 8 chars (letters, numbers, &!@#$%)",
        "recovery_btn_save":         "Save Password",
        "recovery_err_empty_user":   "Please enter your username in the field above first.",
        "recovery_err_fill_all":     "Please fill in both words.",
        "recovery_err_min_length":   "Password must be at least 8 characters.",
        "recovery_err_network":      "Network error. Please check your connection.",
        "recovery_msg_redirect":     " Redirecting...",
        "recovery_err_user_not_found": "User not found.",
        "recovery_err_locked":       "Account recovery is locked for 24 hours due to 3 failed attempts.",
        "recovery_msg_ok":           "Identity verified successfully.",
        "recovery_err_invalid_req":  "Invalid request.",
        "recovery_err_mismatch":     "Words did not match. You have {n} attempt(s) left.",
        "recovery_err_unauthorized": "You are not authorized to perform this action.",
        "recovery_msg_pass_changed": "Password changed successfully.",
        "recovery_err_sys":          "System error occurred.",
        "field_rec_word1":           "Word 1 (e.g. Movie)",
        "field_rec_word2":           "Word 2 (e.g. City)",
        "field_rec_word3":           "Word 3 (e.g. Friend)",
        "register_rec_info":         "Remember these 2 words for recovery (min 5 chars, letters only):",
        "val_rec_word_required":     "Security word is required.",
        "val_rec_word_length":       "Each word must be between 5 and 30 characters.",
        "val_rec_word_format":       "Words may only contain letters (no spaces, numbers, or symbols).",
        "val_rec_word_duplicate":    "Security words cannot be identical.",

    },
}

# ---------------------------------------------------------------------
# ⬛ HELPER FUNCTIONS: Translation lookup and priority localization utilities
# ---------------------------------------------------------------------
def get_translations(language: str = "fa") -> dict:
    """Return the translation dict for the given language code ('fa' or 'en')."""
    return TRANSLATIONS.get(language, TRANSLATIONS["fa"])


def get_localized_priorities(language: str = "fa") -> list:
    """
    Return the default priority list in the active language.
    Storage keys are always the Persian labels ('کم', 'متوسط', 'زیاد').
    This function returns display labels + the storage key for use in dropdowns.
    Returns list of (storage_key, display_label) tuples.
    """
    t = get_translations(language)
    from utils import DEFAULT_PRIORITIES  # avoid circular at module level
    display = [t["priority_low"], t["priority_medium"], t["priority_high"]]
    return list(zip(DEFAULT_PRIORITIES, display))
