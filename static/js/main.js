'use strict';
/**
 * main.js
 *
 * Date-picker strategy
 * --------------------
 * USER_DATE_FMT ('jalali' | 'gregorian') is injected as a const by base.html.
 * USER_LANG_MAIN is read from <html lang="…">.
 *
 * Internal state: always Jalali (backend only accepts "YYYY-MM-DD" Jalali).
 * Display / calendar widget: switches to Gregorian when USER_DATE_FMT === 'gregorian'.
 * Hidden inputs: always Jalali "YYYY-MM-DD" (unchanged backend contract).
 */

// =====================================================================
// FILE: static/js/main.js
// PURPOSE: Core client-side engine for the TaskMen dashboard. Manages task CRUD, real-time UI updates, modals, filtering, drag-and-drop, theme switching, Jalali date pickers, and form validation.
// =====================================================================

// ---------------------------------------------------------------------
// ⬛ GUARD: Check dependencies
// ---------------------------------------------------------------------
if (typeof jalaali === 'undefined') {
  console.error('[main.js] jalaali-js library not found.');
}

// ---------------------------------------------------------------------
// ⬛ LANGUAGE / DATE-FORMAT GLOBALS: Set by base.html inline script
// ---------------------------------------------------------------------
const USER_LANG_MAIN = document.documentElement.lang || 'fa';
// USER_DATE_FMT is a const from base.html — available here as a global.
const IS_GREGORIAN = (typeof USER_DATE_FMT !== 'undefined') && USER_DATE_FMT === 'gregorian';

// ---------------------------------------------------------------------
// ⬛ DIGIT HELPERS: Convert between Persian and English digits
// ---------------------------------------------------------------------
function toPersian(n) {
  return String(n).replace(/[0-9]/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
}
function padPersian(n, w) {
  /* 🎯 استفاده از تابع localizeN به جای toPersian تا زبان سایت در نظر گرفته شود */
  return localizeN(String(n).padStart(w, '0'));
}
function localizeN(n) {
  return USER_LANG_MAIN === 'fa' ? toPersian(n) : String(n);
}

// ---------------------------------------------------------------------
// ⬛ CALENDAR CONSTANTS: Month/weekday names for Jalali and Gregorian
// ---------------------------------------------------------------------
const STYLE_IS_NUMERIC = (typeof USER_DATE_STYLE !== 'undefined') && USER_DATE_STYLE === 'numeric';

const J_MONTHS_FA = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];
const J_MONTHS_EN = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar','Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
const G_MONTHS_FA = ['ژانویه','فوریه','مارس','آوریل','مه','ژوئن','ژوئیه','اوت','سپتامبر','اکتبر','نوامبر','دسامبر'];
const G_MONTHS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December'];

const JALALI_WEEKDAY_NAMES_FA = ['شنبه','یک‌شنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه'];
const GREGORIAN_WEEKDAY_EN = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const JDAY_TO_GDAY_MAP = [6, 0, 1, 2, 3, 4, 5]; // Maps Jalali weekday (0=Sat) to JS Date.getDay() (0=Sun)

// Weekday column headers per combination
const CAL_HDR_JALALI_FA  = ['ش','ی','د','س','چ','پ','ج'];       
const CAL_HDR_JALALI_EN  = ['Sh','Ye','Do','Se','Ch','Pa','Jo']; 
const CAL_HDR_GREG_FA    = ['ش','ی','د','س','چ','پ','ج'];       
const CAL_HDR_GREG_EN    = ['Su','Mo','Tu','We','Th','Fr','Sa']; 

function currentCalHeaders() {
  if (IS_GREGORIAN) return USER_LANG_MAIN === 'fa' ? CAL_HDR_GREG_FA : CAL_HDR_GREG_EN;
  return USER_LANG_MAIN === 'fa' ? CAL_HDR_JALALI_FA : CAL_HDR_JALALI_EN;
}

function getJalaliMonthName(jm) {
  return USER_LANG_MAIN === 'fa' ? J_MONTHS_FA[jm - 1] : J_MONTHS_EN[jm - 1];
}

function getGregorianMonthName(gm) {
  return USER_LANG_MAIN === 'fa' ? G_MONTHS_FA[gm - 1] : G_MONTHS_EN[gm - 1];
}

function getWeekdayName(jy, jm, jd, isGregorianObj = null) {
  if (isGregorianObj) {
    const jsDay = new Date(isGregorianObj.gy, isGregorianObj.gm - 1, isGregorianObj.gd).getDay();
    return USER_LANG_MAIN === 'fa' ? JALALI_WEEKDAY_NAMES_FA[(jsDay + 1) % 7] : GREGORIAN_WEEKDAY_EN[jsDay];
  } else {
    const jWday = jalaliWeekday(jy, jm, jd);
    return USER_LANG_MAIN === 'fa' ? JALALI_WEEKDAY_NAMES_FA[jWday] : GREGORIAN_WEEKDAY_EN[JDAY_TO_GDAY_MAP[jWday]];
  }
}

// ---------------------------------------------------------------------
// ⬛ CONVERSION: Delegate to jalaali-js
// ---------------------------------------------------------------------
function gregorianToJalali(gy, gm, gd) { return jalaali.toJalaali(gy, gm, gd); }
function jalaliToGregorian(jy, jm, jd) { return jalaali.toGregorian(jy, jm, jd); }
function jalaliMonthDays(jy, jm)       { return jalaali.jalaaliMonthLength(jy, jm); }
function gregorianMonthDays(gy, gm)    { return new Date(gy, gm, 0).getDate(); }

/** Today as Jalali {jy,jm,jd} using Tehran wall-clock (+3:30). */
function todayJalali() {
  const tehranMs = Date.now() + new Date().getTimezoneOffset() * 60000 + 210 * 60000;
  const t = new Date(tehranMs);
  return gregorianToJalali(t.getFullYear(), t.getMonth() + 1, t.getDate());
}

/** Today as Gregorian {gy,gm,gd} using Tehran wall-clock. */
function todayGregorian() {
  const tehranMs = Date.now() + new Date().getTimezoneOffset() * 60000 + 210 * 60000;
  const t = new Date(tehranMs);
  return { gy: t.getFullYear(), gm: t.getMonth() + 1, gd: t.getDate() };
}

/** Jalali weekday: 0=Saturday … 6=Friday */
function jalaliWeekday(jy, jm, jd) {
  const { gy, gm, gd } = jalaliToGregorian(jy, jm, jd);
  return (new Date(gy, gm - 1, gd).getDay() + 1) % 7;
}

/**
 * Gregorian weekday offset for the first day of the month.
 * FA locale: 0=Saturday … 6=Friday (RTL, week starts Sat)
 * EN locale: 0=Sunday  … 6=Saturday (LTR, week starts Sun)
 */
function gregorianFirstWeekday(gy, gm) {
  const jsDay = new Date(gy, gm - 1, 1).getDay(); // 0=Sun…6=Sat
  return USER_LANG_MAIN === 'fa' ? (jsDay + 1) % 7 : jsDay;
}

function jalaliFirstWeekday(jy, jm) { return jalaliWeekday(jy, jm, 1); }

// ---------------------------------------------------------------------
// ⬛ JALALICALENDAR WIDGET: Jalali UI
// ---------------------------------------------------------------------
class JalaliCalendar {
  constructor({ calPopupId, calDaysId, calLabelId, prevId, nextId, onSelect, disablePast = false }) {
    this.popup   = document.getElementById(calPopupId);
    this.daysEl  = document.getElementById(calDaysId);
    this.labelEl = document.getElementById(calLabelId);
    this.prevBtn = document.getElementById(prevId);
    this.nextBtn = document.getElementById(nextId);
    this.onSelect    = onSelect;
    this.disablePast = disablePast;

    const today = todayJalali();
    this.todayJy = today.jy; this.todayJm = today.jm; this.todayJd = today.jd;
    this.viewJy  = today.jy; this.viewJm  = today.jm;
    this.selectedJy = null; this.selectedJm = null; this.selectedJd = null;

    if (this.prevBtn) this.prevBtn.addEventListener('click', () => this._prevMonth());
    if (this.nextBtn) this.nextBtn.addEventListener('click', () => this._nextMonth());

    this._renderHeaders();
  }

  _renderHeaders() {
    if (!this.popup) return;
    const wdEl = this.popup.querySelector('.cal-weekdays');
    if (!wdEl) return;
    const hdrs = USER_LANG_MAIN === 'fa' ? CAL_HDR_JALALI_FA : CAL_HDR_JALALI_EN;
    wdEl.innerHTML = hdrs.map(h => `<span>${h}</span>`).join('');
  }

  _prevMonth() { this.viewJm--; if (this.viewJm < 1)  { this.viewJm = 12; this.viewJy--; } this.render(); }
  _nextMonth() { this.viewJm++; if (this.viewJm > 12) { this.viewJm = 1;  this.viewJy++; } this.render(); }

  /** Returns true if Jalali date (jy,jm,jd) is strictly before today. */
  _isDayPast(jy, jm, jd) {
    if (jy < this.todayJy) return true;
    if (jy === this.todayJy && jm < this.todayJm) return true;
    if (jy === this.todayJy && jm === this.todayJm && jd < this.todayJd) return true;
    return false;
  }

  setSelected(jy, jm, jd) {
    this.selectedJy = jy; this.selectedJm = jm; this.selectedJd = jd;
    this.viewJy = jy; this.viewJm = jm;
  }

  selectToday() {
    const t = todayJalali();
    this.setSelected(t.jy, t.jm, t.jd);
  }

  render() {
    if (!this.daysEl || !this.labelEl) return;
    const jy = this.viewJy, jm = this.viewJm;
    const mName = getJalaliMonthName(jm);
    this.labelEl.textContent = `${mName} ${localizeN(jy)}`;

    const totalDays = jalaliMonthDays(jy, jm);
    const firstWday = jalaliFirstWeekday(jy, jm);
    this.daysEl.innerHTML = '';

    for (let i = 0; i < firstWday; i++) {
      const e = document.createElement('span'); e.className = 'cal-day empty';
      this.daysEl.appendChild(e);
    }

    const isCurrent = this.todayJy === jy && this.todayJm === jm;
    for (let d = 1; d <= totalDays; d++) {
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'cal-day';
      btn.textContent = localizeN(d);
      btn.setAttribute('aria-label', `${d} ${mName} ${localizeN(jy)}`);
      if (isCurrent && d === this.todayJd) btn.classList.add('today');
      if (this.selectedJy === jy && this.selectedJm === jm && this.selectedJd === d) btn.classList.add('selected');

      if (this.disablePast && this._isDayPast(jy, jm, d)) {
        btn.disabled = true;
      } else {
        btn.addEventListener('click', () => {
          this.selectedJy = jy; this.selectedJm = jm; this.selectedJd = d;
          this.render();
          if (this.onSelect) this.onSelect(jy, jm, d);
        });
      }

      this.daysEl.appendChild(btn);
    }
  }

  show()   { if (this.popup) { this.popup.classList.remove('hidden'); this.render(); } }
  hide()   { if (this.popup) this.popup.classList.add('hidden'); }
  toggle() { if (this.popup && this.popup.classList.contains('hidden')) this.show(); else this.hide(); }
}

// ---------------------------------------------------------------------
// ⬛ GREGORIANCALENDAR WIDGET: Same API as JalaliCalendar, returns Gregorian coordinates
// ---------------------------------------------------------------------
class GregorianCalendar {
  constructor({ calPopupId, calDaysId, calLabelId, prevId, nextId, onSelect, disablePast = false }) {
    this.popup   = document.getElementById(calPopupId);
    this.daysEl  = document.getElementById(calDaysId);
    this.labelEl = document.getElementById(calLabelId);
    this.prevBtn = document.getElementById(prevId);
    this.nextBtn = document.getElementById(nextId);
    this.onSelect    = onSelect;
    this.disablePast = disablePast;

    const today = todayGregorian();
    this.todayGy = today.gy; this.todayGm = today.gm; this.todayGd = today.gd;
    this.viewGy  = today.gy; this.viewGm  = today.gm;
    this.selectedGy = null; this.selectedGm = null; this.selectedGd = null;

    if (this.prevBtn) this.prevBtn.addEventListener('click', () => this._prevMonth());
    if (this.nextBtn) this.nextBtn.addEventListener('click', () => this._nextMonth());

    this._renderHeaders();
  }

  _renderHeaders() {
    if (!this.popup) return;
    const wdEl = this.popup.querySelector('.cal-weekdays');
    if (!wdEl) return;
    const hdrs = USER_LANG_MAIN === 'fa' ? CAL_HDR_GREG_FA : CAL_HDR_GREG_EN;
    wdEl.innerHTML = hdrs.map(h => `<span>${h}</span>`).join('');
  }

  _prevMonth() { this.viewGm--; if (this.viewGm < 1)  { this.viewGm = 12; this.viewGy--; } this.render(); }
  _nextMonth() { this.viewGm++; if (this.viewGm > 12) { this.viewGm = 1;  this.viewGy++; } this.render(); }

  /** Returns true if Gregorian date (gy,gm,gd) is strictly before today. */
  _isDayPast(gy, gm, gd) {
    if (gy < this.todayGy) return true;
    if (gy === this.todayGy && gm < this.todayGm) return true;
    if (gy === this.todayGy && gm === this.todayGm && gd < this.todayGd) return true;
    return false;
  }

  setSelected(gy, gm, gd) {
    this.selectedGy = gy; this.selectedGm = gm; this.selectedGd = gd;
    this.viewGy = gy; this.viewGm = gm;
  }

  selectToday() {
    const t = todayGregorian();
    this.setSelected(t.gy, t.gm, t.gd);
  }

  render() {
    if (!this.daysEl || !this.labelEl) return;
    const gy = this.viewGy, gm = this.viewGm;
    const mName = getGregorianMonthName(gm);
    this.labelEl.textContent = `${mName} ${localizeN(gy)}`;

    const totalDays = gregorianMonthDays(gy, gm);
    const firstWday = gregorianFirstWeekday(gy, gm);
    this.daysEl.innerHTML = '';

    for (let i = 0; i < firstWday; i++) {
      const e = document.createElement('span'); e.className = 'cal-day empty';
      this.daysEl.appendChild(e);
    }

    const isCurrent = this.todayGy === gy && this.todayGm === gm;
    for (let d = 1; d <= totalDays; d++) {
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'cal-day';
      btn.textContent = localizeN(d);
      btn.setAttribute('aria-label', `${d} ${mName} ${localizeN(gy)}`);
      if (isCurrent && d === this.todayGd) btn.classList.add('today');
      if (this.selectedGy === gy && this.selectedGm === gm && this.selectedGd === d) btn.classList.add('selected');

      if (this.disablePast && this._isDayPast(gy, gm, d)) {
        btn.disabled = true;
      } else {
        btn.addEventListener('click', () => {
          this.selectedGy = gy; this.selectedGm = gm; this.selectedGd = d;
          this.render();
          if (this.onSelect) this.onSelect(gy, gm, d);
        });
      }

      this.daysEl.appendChild(btn);
    }
  }

  show()   { if (this.popup) { this.popup.classList.remove('hidden'); this.render(); } }
  hide()   { if (this.popup) this.popup.classList.add('hidden'); }
  toggle() { if (this.popup && this.popup.classList.contains('hidden')) this.show(); else this.hide(); }
}

/** Factory: returns JalaliCalendar or GregorianCalendar based on IS_GREGORIAN.
 *  Passes disablePast through to the calendar. */
function makeCalendar(cfg) {
  return IS_GREGORIAN ? new GregorianCalendar(cfg) : new JalaliCalendar(cfg);
}

// ---------------------------------------------------------------------
// ⬛ TIMEPICKER WIDGET: 12-hour AM/PM to 24-hour output
// ---------------------------------------------------------------------
class TimePicker {
  constructor({ popupId, hrId, mnId, ampmId, confirmId, onConfirm }) {
    this.popup      = document.getElementById(popupId);
    this.hrEl       = document.getElementById(hrId);
    this.mnEl       = document.getElementById(mnId);
    this.ampmEl     = document.getElementById(ampmId);
    this.confirmBtn = document.getElementById(confirmId);
    this.onConfirm  = onConfirm;

    this._hh = 12; this._mm = 0; this._isPm = true;

    // Min-time: only valid when today is selected in the calendar
    this._minHour24 = null;   // 0–23, null = no minimum
    this._minMin    = null;   // 0–59, null = no minimum

    if (this.popup) {
      this.popup.querySelectorAll('.time-arrow').forEach(btn => {
        btn.addEventListener('click', () => {
          const dir = btn.getAttribute('data-dir');
          const tgt = btn.getAttribute('data-target');
          if (tgt === hrId) this._changeHour(dir === 'up' ? 1 : -1);
          if (tgt === mnId) this._changeMinute(dir === 'up' ? 5 : -5);
        });
      });
    }
    if (this.ampmEl) {
      this.ampmEl.addEventListener('click', () => {
        this._isPm = !this._isPm;
        // Re-clamp after AM↔PM switch
        if (this._minHour24 !== null) this._clampToMin();
        this._render();
      });
    }
    if (this.confirmBtn) {
      this.confirmBtn.addEventListener('click', () => {
        // Final clamp before firing callback
        if (this._minHour24 !== null) this._clampToMin();
        this.hide();
        if (this.onConfirm) this.onConfirm(this._to24(), this._mm);
      });
    }
  }

  _to24() { let h = this._hh % 12; if (this._isPm) h += 12; return h; }

  _changeHour(d) {
    this._hh = ((this._hh - 1 + d + 12) % 12) + 1;
    if (this._minHour24 !== null) this._clampToMin();
    this._render();
  }
  _changeMinute(d) {
    this._mm = (this._mm + d + 60) % 60;
    if (this._minHour24 !== null) this._clampToMin();
    this._render();
  }

  /**
   * Clamp _hh/_mm/_isPm so that _to24():_mm >= _minHour24:_minMin.
   * If current 24h time < min, snap to the minimum.
   */
  _clampToMin() {
    if (this._minHour24 === null) return;
    const cur24 = this._to24();
    const minH  = this._minHour24;
    const minM  = this._minMin || 0;
    if (cur24 < minH || (cur24 === minH && this._mm < minM)) {
      // Snap to minimum: convert minH to 12h
      this._mm = minM;
      if (minH === 0)       { this._hh = 12; this._isPm = false; }
      else if (minH < 12)  { this._hh = minH; this._isPm = false; }
      else if (minH === 12) { this._hh = 12;  this._isPm = true; }
      else                  { this._hh = minH - 12; this._isPm = true; }
    }
  }

  _render() {
    if (this.hrEl)   this.hrEl.textContent   = localizeN(this._hh);
    if (this.mnEl)   this.mnEl.textContent   = padPersian(this._mm, 2);
    if (this.ampmEl) {
      const pmLabel = (window.I18N && window.I18N.js_pm) ? window.I18N.js_pm : 'ب.ظ';
      const amLabel = (window.I18N && window.I18N.js_am) ? window.I18N.js_am : 'ق.ظ';
      this.ampmEl.textContent = this._isPm ? pmLabel : amLabel;
    }
  }

  /**
   * Called by PickerController when today is selected.
   * Clamps current spinner values immediately.
   */
  setMinTime(hh24, mm) {
    this._minHour24 = hh24;
    this._minMin    = mm;
    this._clampToMin();
    this._render();
  }

  /** Called when a future date is selected — remove the minimum. */
  clearMinTime() {
    this._minHour24 = null;
    this._minMin    = null;
  }

  setTime(hh24, mm) {
    this._mm = mm;
    if (hh24 === 0)       { this._hh = 12; this._isPm = false; }
    else if (hh24 < 12)   { this._hh = hh24; this._isPm = false; }
    else if (hh24 === 12) { this._hh = 12;   this._isPm = true; }
    else                  { this._hh = hh24 - 12; this._isPm = true; }
    this._render();
  }

  show()   { if (this.popup) { this.popup.classList.remove('hidden'); this._render(); } }
  hide()   { if (this.popup) this.popup.classList.add('hidden'); }
  toggle() { if (this.popup && this.popup.classList.contains('hidden')) this.show(); else this.hide(); }
}

// ---------------------------------------------------------------------
// ⬛ DURATIONPICKER WIDGET: HH:MM spinner for estimated_time
// ---------------------------------------------------------------------
class DurationPicker {
  constructor({ boxId, displayId, hiddenId, popupId, hrId, mnId, confirmId, notSetLabel }) {
    this.box        = document.getElementById(boxId);
    this.display    = document.getElementById(displayId);
    this.hidden     = document.getElementById(hiddenId);
    this.popup      = document.getElementById(popupId);
    this.hrEl       = document.getElementById(hrId);
    this.mnEl       = document.getElementById(mnId);
    this.confirmBtn = document.getElementById(confirmId);
    this.notSetLabel = notSetLabel || '—';

    this._hh = 0;  // 0–23
    this._mm = 0;  // 0,5,10,…,55

    // Arrow buttons
    if (this.popup) {
      this.popup.querySelectorAll('.time-arrow').forEach(btn => {
        btn.addEventListener('click', () => {
          const dir = btn.getAttribute('data-dir');
          const tgt = btn.getAttribute('data-target');
          if (tgt === hrId) this._changeHour(dir === 'up' ? 1 : -1);
          if (tgt === mnId) this._changeMinute(dir === 'up' ? 5 : -5);
        });
      });
    }

    // Confirm
    if (this.confirmBtn) {
      this.confirmBtn.addEventListener('click', () => {
        this.hide();
        const totalMin = this._hh * 60 + this._mm;
        if (this.hidden) this.hidden.value = totalMin;
        this._renderDisplay(this._hh, this._mm);
      });
    }

    // Toggle on box click
    if (this.box) {
      this.box.addEventListener('click', () => this.toggle());
      this.box.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.box.click(); }
      });
    }

    // Close on outside click
    document.addEventListener('click', e => {
      if (this.popup && !this.popup.contains(e.target) && !this.box?.contains(e.target)) {
        this.hide();
      }
    });
  }

  _changeHour(d)   { this._hh = ((this._hh + d) + 24) % 24; this._render(); }
  _changeMinute(d) { this._mm = ((this._mm + d) + 60) % 60; this._render(); }

  _render() {
    if (this.hrEl) this.hrEl.textContent = localizeN(this._hh);
    if (this.mnEl) this.mnEl.textContent = padPersian(this._mm, 2);
  }

  _renderDisplay(hh, mm) {
    if (!this.display) return;
    if (hh === 0 && mm === 0) {
      this.display.textContent = this.notSetLabel;
      return;
    }
    const parts = [];
    if (hh > 0) parts.push(`${localizeN(hh)}h`);
    if (mm > 0) parts.push(`${localizeN(mm)}m`);
    this.display.textContent = parts.join(' ');
  }

  /** Pre-fill from a total-minutes integer (e.g. from data-estimated on edit button). */
  prefill(totalMin) {
    const m = parseInt(totalMin, 10);
    if (isNaN(m) || m < 0) return;
    this._hh = Math.min(Math.floor(m / 60), 23);
    this._mm = Math.round((m % 60) / 5) * 5 % 60;  // snap to nearest 5
    if (this.hidden) this.hidden.value = m;
    this._render();
    this._renderDisplay(this._hh, this._mm);
  }

  /** Reset to 0h 0m — called when create-modal opens. */
  reset() {
    this._hh = 0; this._mm = 0;
    if (this.hidden) this.hidden.value = '';
    this._render();
    if (this.display) this.display.textContent = this.notSetLabel;
  }

  show()   { if (this.popup) { this.popup.classList.remove('hidden'); this._render(); } }
  hide()   { if (this.popup) this.popup.classList.add('hidden'); }
  toggle() { if (this.popup && this.popup.classList.contains('hidden')) this.show(); else this.hide(); }
}

// ---------------------------------------------------------------------
// ⬛ PICKERCONTROLLER: Wires date + time boxes to hidden input
// ---------------------------------------------------------------------
class PickerController {
  constructor(cfg) {
    this.cfg         = cfg;
    this.hiddenInput = document.getElementById(cfg.hiddenId);
    this.dateBox     = document.getElementById(cfg.dateBoxId);
    this.timeBox     = document.getElementById(cfg.timeBoxId);
    this.dateDisplay = document.getElementById(cfg.dateDisplayId);
    this.timeDisplay = document.getElementById(cfg.timeDisplayId);
    this.summaryText = document.getElementById(cfg.summaryTextId);

    // Internal state: always Jalali
    this._jy = null; this._jm = null; this._jd = null;
    this._hh24 = null; this._mm = null;

    // GregorianCalendar onSelect gives (gy,gm,gd) → convert to Jalali
    // JalaliCalendar onSelect gives (jy,jm,jd) → store directly
    const calOnSelect = IS_GREGORIAN
      ? (gy, gm, gd) => {
          const j = gregorianToJalali(gy, gm, gd);
          this._jy = j.jy; this._jm = j.jm; this._jd = j.jd;
          this.cal.hide();
          this._notifyTimePicker();
          this._updateDisplay();
        }
      : (jy, jm, jd) => {
          this._jy = jy; this._jm = jm; this._jd = jd;
          this.cal.hide();
          this._notifyTimePicker();
          this._updateDisplay();
        };

    this.cal = makeCalendar({
      calPopupId:  cfg.calPopupId,
      calDaysId:   cfg.calDaysId,
      calLabelId:  cfg.calLabelId,
      prevId:      cfg.calPrevId,
      nextId:      cfg.calNextId,
      onSelect:    calOnSelect,
      disablePast: cfg.disablePast || false,
    });

    this.time = new TimePicker({
      popupId:   cfg.timePopupId,
      hrId:      cfg.hrId,
      mnId:      cfg.mnId,
      ampmId:    cfg.ampmId,
      confirmId: cfg.timeConfirmId,
      onConfirm: (hh24, mm) => { this._hh24 = hh24; this._mm = mm; this._updateDisplay(); },
    });

    if (this.dateBox) {
      this.dateBox.addEventListener('click', () => { this.time.hide(); this.cal.toggle(); });
      this.dateBox.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.dateBox.click(); }
      });
    }
    if (this.timeBox) {
      this.timeBox.addEventListener('click', () => { this.cal.hide(); this.time.toggle(); });
      this.timeBox.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.timeBox.click(); }
      });
    }

    document.addEventListener('click', e => {
      const calPopup  = document.getElementById(cfg.calPopupId);
      const timePopup = document.getElementById(cfg.timePopupId);
      if (calPopup  && !calPopup.contains(e.target)  && !this.dateBox?.contains(e.target))  this.cal.hide();
      if (timePopup && !timePopup.contains(e.target) && !this.timeBox?.contains(e.target)) this.time.hide();
    });
  }

  /**
   * Pre-fill from a "YYYY-MM-DD" Jalali string (from server/edit form).
   */
  prefill(expiresStr) {
    if (!expiresStr) return;
    
    // تبدیل اعداد فارسی به انگلیسی برای جلوگیری از خطای خواندن تاریخ
    const engStr = String(expiresStr).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
    
    const [jy, jm, jd] = engStr.split('-').map(Number);
    if (!jy || !jm || !jd) return;
    this._jy = jy; this._jm = jm; this._jd = jd;

    if (IS_GREGORIAN) {
      const { gy, gm, gd } = jalaliToGregorian(jy, jm, jd);
      this.cal.setSelected(gy, gm, gd);
    } else {
      this.cal.setSelected(jy, jm, jd);
    }
    this._updateDisplay();
  }

  /** Returns true if the stored Jalali date (_jy/_jm/_jd) equals today. */
  _isSelectedToday() {
    if (!this._jy || !this._jm || !this._jd) return false;
    const t = todayJalali();
    return this._jy === t.jy && this._jm === t.jm && this._jd === t.jd;
  }

  /**
   * Tell the TimePicker the current min-time constraint.
   * Called after every date selection and on resetToToday.
   * Only applies when cfg.disablePast is true (create modal).
   */
  _notifyTimePicker() {
    if (!this.cfg.disablePast) return;
    if (this._isSelectedToday()) {
      const now = new Date();
      // Round up to the next 5-min slot so there's room to confirm
      let minH = now.getHours();
      let minM = Math.ceil(now.getMinutes() / 5) * 5;
      if (minM >= 60) { minM = 0; minH = Math.min(minH + 1, 23); }
      this.time.setMinTime(minH, minM);
    } else {
      this.time.clearMinTime();
    }
  }

  /** Select today and navigate calendar. Called when create-modal opens. */
  resetToToday() {
    const t = todayJalali();
    this._jy = t.jy; this._jm = t.jm; this._jd = t.jd;
    this._hh24 = null; this._mm = null;
    this.cal.selectToday();
    this._notifyTimePicker();
    this._updateDisplay();
  }

  _updateDisplay() {
    if (this._jy !== null && this.dateDisplay) {
      this.dateDisplay.textContent = this._formatDate(this._jy, this._jm, this._jd);
    }
    if (this._hh24 !== null && this.timeDisplay) {
      this.timeDisplay.textContent = `${padPersian(this._hh24, 2)}:${padPersian(this._mm, 2)}`;
    }
    this._buildSummary();
    this._assembleHidden();
  }

  /** Format a Jalali date for display (Jalali or Gregorian depending on setting). */
  _formatDate(jy, jm, jd) {
    if (IS_GREGORIAN) {
      const { gy, gm, gd } = jalaliToGregorian(jy, jm, jd);
      if (STYLE_IS_NUMERIC) return `${localizeN(gy)}/${padPersian(gm, 2)}/${padPersian(gd, 2)}`;
      return `${localizeN(gd)} ${getGregorianMonthName(gm)} ${localizeN(gy)}`;
    }
    if (STYLE_IS_NUMERIC) return `${localizeN(jy)}/${padPersian(jm, 2)}/${padPersian(jd, 2)}`;
    return `${localizeN(jd)} ${getJalaliMonthName(jm)} ${localizeN(jy)}`;
  }

  _buildSummary() {
    if (!this.summaryText) return;
    if (this._jy === null) {
      this.summaryText.textContent =
        (window.I18N && window.I18N.js_not_selected)
          ? window.I18N.js_not_selected
          : '— انتخاب نشده —';
      return;
    }

    let wdName, dateLabel;
    if (IS_GREGORIAN) {
      const { gy, gm, gd } = jalaliToGregorian(this._jy, this._jm, this._jd);
      wdName = getWeekdayName(this._jy, this._jm, this._jd, {gy, gm, gd});
      if (STYLE_IS_NUMERIC) {
        dateLabel = `${wdName} ${localizeN(gy)}/${padPersian(gm, 2)}/${padPersian(gd, 2)}`;
      } else {
        dateLabel = `${wdName} ${localizeN(gd)} ${getGregorianMonthName(gm)} ${localizeN(gy)}`;
      }
    } else {
      wdName = getWeekdayName(this._jy, this._jm, this._jd);
      if (STYLE_IS_NUMERIC) {
        dateLabel = `${wdName} ${localizeN(this._jy)}/${padPersian(this._jm, 2)}/${padPersian(this._jd, 2)}`;
      } else {
        dateLabel = `${wdName} ${localizeN(this._jd)} ${getJalaliMonthName(this._jm)} ${localizeN(this._jy)}`;
      }
    }

    const timeStr = this._hh24 !== null
      ? ` - ${padPersian(this._hh24, 2)}:${padPersian(this._mm, 2)}`
      : '';

    this.summaryText.textContent = `${dateLabel}${timeStr}`;
  }

  /** Hidden input always receives Jalali "YYYY-MM-DD[ HH:MM]". */
  _assembleHidden() {
    if (!this.hiddenInput || this._jy === null) return;
    const dateStr = `${this._jy}-${String(this._jm).padStart(2,'0')}-${String(this._jd).padStart(2,'0')}`;
    this.hiddenInput.value = this._hh24 !== null
      ? `${dateStr} ${String(this._hh24).padStart(2,'0')}:${String(this._mm).padStart(2,'0')}`
      : dateStr;
  }
}

// ---------------------------------------------------------------------
// ⬛ FILTERDATEPICKER: Date-only picker for GET filter forms
// ---------------------------------------------------------------------
class FilterDatePicker {
  constructor({ boxId, displayId, hiddenId, calPopupId, calDaysId, calLabelId, prevId, nextId }) {
    this.box      = document.getElementById(boxId);
    this.display  = document.getElementById(displayId);
    this.hidden   = document.getElementById(hiddenId);
    this.calPopup = document.getElementById(calPopupId);

    // GregorianCalendar onSelect(gy,gm,gd) → convert to Jalali for hidden
    // JalaliCalendar  onSelect(jy,jm,jd)  → use directly
    const onSelect = IS_GREGORIAN
      ? (gy, gm, gd) => {
          this.cal.hide();
          const j = gregorianToJalali(gy, gm, gd);
          this._writeHiddenJalali(j.jy, j.jm, j.jd);
          this._renderDisplay(gy, gm, gd, true);
        }
      : (jy, jm, jd) => {
          this.cal.hide();
          this._writeHiddenJalali(jy, jm, jd);
          this._renderDisplay(jy, jm, jd, false);
        };

    this.cal = makeCalendar({ calPopupId, calDaysId, calLabelId, prevId, nextId, onSelect });

    if (this.box) {
      this.box.addEventListener('click', () => this.cal.toggle());
      this.box.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.box.click(); }
      });
    }

    document.addEventListener('click', e => {
      if (this.calPopup && !this.calPopup.contains(e.target) && !this.box?.contains(e.target)) {
        this.cal.hide();
      }
    });

    // Pre-fill from existing query-param value (Jalali YYYY-MM-DD)
    if (this.hidden && this.hidden.value) this._prefill(this.hidden.value);
  }

  /** Parse Jalali "YYYY-MM-DD" from query param, pre-select in calendar, show display. */
  _prefill(str) {
    if (!str) return;
    const [jy, jm, jd] = str.split('-').map(Number);
    if (!jy || !jm || !jd) return;

    if (IS_GREGORIAN) {
      const { gy, gm, gd } = jalaliToGregorian(jy, jm, jd);
      this.cal.setSelected(gy, gm, gd);
      this._renderDisplay(gy, gm, gd, true);
    } else {
      this.cal.setSelected(jy, jm, jd);
      this._renderDisplay(jy, jm, jd, false);
    }
  }

  _writeHiddenJalali(jy, jm, jd) {
    if (this.hidden) {
      this.hidden.value = `${jy}-${String(jm).padStart(2,'0')}-${String(jd).padStart(2,'0')}`;
    }
  }

  /** isGreg=true → (gy,gm,gd); isGreg=false → (jy,jm,jd) */
  _renderDisplay(y, m, d, isGreg) {
    if (!this.display) return;
    if (isGreg) {
      if (STYLE_IS_NUMERIC) {
        this.display.textContent = `${localizeN(y)}/${padPersian(m, 2)}/${padPersian(d, 2)}`;
      } else {
        this.display.textContent = `${localizeN(d)} ${getGregorianMonthName(m)} ${localizeN(y)}`;
      }
    } else {
      if (STYLE_IS_NUMERIC) {
        this.display.textContent = `${localizeN(y)}/${padPersian(m, 2)}/${padPersian(d, 2)}`;
      } else {
        this.display.textContent = `${localizeN(d)} ${getJalaliMonthName(m)} ${localizeN(y)}`;
      }
    }
  }
}

// ---------------------------------------------------------------------
// ⬛ MODAL PICKERS: Instantiate pickers for create and edit modals
// ---------------------------------------------------------------------
let createPicker = null;
let editPicker   = null;

if (document.getElementById('ct_cal_popup')) {
  createPicker = new PickerController({
    hiddenId:      'ct_expires_at_hidden',
    dateBoxId:     'ct_date_box',
    timeBoxId:     'ct_time_box',
    dateDisplayId: 'ct_date_display',
    timeDisplayId: 'ct_time_display',
    summaryTextId: 'ct_summary_text',
    calPopupId:    'ct_cal_popup',
    calDaysId:     'ct_cal_days',
    calLabelId:    'ct_cal_label',
    calPrevId:     'ct_cal_prev',
    calNextId:     'ct_cal_next',
    timePopupId:   'ct_time_popup',
    hrId:          'ct_hr',
    mnId:          'ct_mn',
    ampmId:        'ct_ampm',
    timeConfirmId: 'ct_time_confirm',
    disablePast:   true,   // create modal: no past dates allowed
  });
}

if (document.getElementById('et_cal_popup')) {
  editPicker = new PickerController({
    hiddenId:      'et_expires_at_hidden',
    dateBoxId:     'et_date_box',
    timeBoxId:     'et_time_box',
    dateDisplayId: 'et_date_display',
    timeDisplayId: 'et_time_display',
    summaryTextId: 'et_summary_text',
    calPopupId:    'et_cal_popup',
    calDaysId:     'et_cal_days',
    calLabelId:    'et_cal_label',
    calPrevId:     'et_cal_prev',
    calNextId:     'et_cal_next',
    timePopupId:   'et_time_popup',
    hrId:          'et_hr',
    mnId:          'et_mn',
    ampmId:        'et_ampm',
    timeConfirmId: 'et_time_confirm',
    disablePast:   true,   // edit modal: same restriction as create
  });
}

// ---------------------------------------------------------------------
// ⬛ DURATION PICKERS: Instantiate duration pickers for estimated_time
// ---------------------------------------------------------------------
const NOT_SET_LABEL = (window.I18N && window.I18N.est_not_set) ? window.I18N.est_not_set : '—';

let createDurPicker = null;
let editDurPicker   = null;

if (document.getElementById('ct_est_popup')) {
  createDurPicker = new DurationPicker({
    boxId:      'ct_est_box',
    displayId:  'ct_est_display',
    hiddenId:   'ct_estimated_time',
    popupId:    'ct_est_popup',
    hrId:       'ct_est_hr',
    mnId:       'ct_est_mn',
    confirmId:  'ct_est_confirm',
    notSetLabel: NOT_SET_LABEL,
  });
}

if (document.getElementById('et_est_popup')) {
  editDurPicker = new DurationPicker({
    boxId:      'et_est_box',
    displayId:  'et_est_display',
    hiddenId:   'et_estimated_time',
    popupId:    'et_est_popup',
    hrId:       'et_est_hr',
    mnId:       'et_est_mn',
    confirmId:  'et_est_confirm',
    notSetLabel: NOT_SET_LABEL,
  });
}

// ---------------------------------------------------------------------
// ⬛ INDEX FILTER PICKERS: Instantiate filter date pickers — index page
// ---------------------------------------------------------------------
if (document.getElementById('startDateCal')) {
  new FilterDatePicker({
    boxId: 'startDateBox', displayId: 'startDateDisplay', hiddenId: 'startDateHidden',
    calPopupId: 'startDateCal', calDaysId: 'startDateCalDays', calLabelId: 'startDateCalLabel',
    prevId: 'startDateCalPrev', nextId: 'startDateCalNext',
  });
}
if (document.getElementById('endDateCal')) {
  new FilterDatePicker({
    boxId: 'endDateBox', displayId: 'endDateDisplay', hiddenId: 'endDateHidden',
    calPopupId: 'endDateCal', calDaysId: 'endDateCalDays', calLabelId: 'endDateCalLabel',
    prevId: 'endDateCalPrev', nextId: 'endDateCalNext',
  });
}

// ---------------------------------------------------------------------
// ⬛ ANALYTICS FILTER PICKERS: Instantiate filter date pickers — analytics page
// ---------------------------------------------------------------------
if (document.getElementById('aStartDateCal')) {
  new FilterDatePicker({
    boxId: 'aStartDateBox', displayId: 'aStartDateDisplay', hiddenId: 'aStartDateHidden',
    calPopupId: 'aStartDateCal', calDaysId: 'aStartDateCalDays', calLabelId: 'aStartDateCalLabel',
    prevId: 'aStartDateCalPrev', nextId: 'aStartDateCalNext',
  });
}
if (document.getElementById('aEndDateCal')) {
  new FilterDatePicker({
    boxId: 'aEndDateBox', displayId: 'aEndDateDisplay', hiddenId: 'aEndDateHidden',
    calPopupId: 'aEndDateCal', calDaysId: 'aEndDateCalDays', calLabelId: 'aEndDateCalLabel',
    prevId: 'aEndDateCalPrev', nextId: 'aEndDateCalNext',
  });
}

// ---------------------------------------------------------------------
// ⬛ TOAST VALIDATION: Validate before submit using Toast
// ---------------------------------------------------------------------
function showJSToast(msg) {
  const container = document.querySelector('.flash-toast-container');
  if (!container) { 
    console.error('Toast container not found!'); 
    return; 
  }
  
  const toast = document.createElement('div');
  toast.className = 'flash-toast flash-danger';
  toast.innerHTML = `
    <span class="toast-text">${msg}</span>
    <button type="button" class="toast-close" aria-label="✕" onclick="this.parentElement.remove()">✕</button>
  `;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// --- ▷ اعتبارسنجی و رفتار هوشمند فرم ایجاد تسک (Create): Validate create task form ---
const createForm = document.getElementById('createTaskForm');

// تابع تنظیم ارتفاع خودکار (Auto-resize)
function autoResize(el) {
  if (!el) return;
  el.style.height = 'auto'; // ریست کردن ارتفاع
  el.style.height = (el.scrollHeight) + 'px'; // تنظیم ارتفاع بر اساس محتوا
}

// تابع بررسی محدودیت کاراکتر و قرمز کردن ظاهر باکس
function checkLimits(el, maxLimit) {
  if (!el) return;
  if (el.value.length > maxLimit) {
    el.style.borderColor = '#ff4d4d'; // حاشیه قرمز
    el.style.color = '#ff4d4d';       // متن قرمز
    el.style.backgroundColor = 'rgba(255, 77, 77, 0.05)'; // پس‌زمینه محو قرمز
  } else {
    el.style.borderColor = '';
    el.style.color = '';
    el.style.backgroundColor = '';
  }
}

let ctTitle = document.getElementById('ct_title');
let ctDesc = document.getElementById('ct_description');

// 🎯 حذف محدودیت‌های سخت‌گیرانه HTML تا کاربر بتواند آزادانه تایپ کند
if (ctTitle) ctTitle.removeAttribute('maxlength');
if (ctDesc) ctDesc.removeAttribute('maxlength');

// جادو: تبدیل اینپوت یک‌خطیِ عنوان به تکست‌اریا تا بتواند ارتفاعش زیاد شود
if (ctTitle && ctTitle.tagName.toLowerCase() === 'input') {
  const textareaTitle = document.createElement('textarea');
  textareaTitle.id = ctTitle.id;
  textareaTitle.name = ctTitle.name;
  textareaTitle.className = ctTitle.className;
  textareaTitle.placeholder = ctTitle.placeholder;
  textareaTitle.value = ctTitle.value;
  textareaTitle.setAttribute('rows', '1');
  textareaTitle.style.resize = 'none'; // بستن قابلیت کشیدن دستی
  textareaTitle.style.overflow = 'hidden'; // مخفی کردن اسکرول‌بار
  ctTitle.parentNode.replaceChild(textareaTitle, ctTitle);
  ctTitle = textareaTitle; // آپدیت کردن متغیر
}

// استایل اولیه برای باکس توضیحات
if (ctDesc) {
  ctDesc.style.resize = 'none';
  ctDesc.style.overflow = 'hidden';
}

// واکنش زنده هنگام تایپ کردن کاربر
if (ctTitle) {
  ctTitle.addEventListener('input', function() {
    autoResize(this);
    checkLimits(this, 100);
  });
  setTimeout(() => autoResize(ctTitle), 100);
}

if (ctDesc) {
  ctDesc.addEventListener('input', function() {
    autoResize(this);
    checkLimits(this, 500);
  });
  setTimeout(() => autoResize(ctDesc), 100);
}

// بررسی نهایی هنگام کلیک روی دکمه ذخیره
if (createForm) {
  createForm.addEventListener('submit', function (e) {
    const isFa = document.documentElement.lang === 'fa' || window.USER_LANG_MAIN === 'fa';
    
    // ۱. بررسی عنوان
    if (ctTitle) {
      const titleVal = ctTitle.value.trim();
      if (!titleVal) {
        e.preventDefault(); // متوقف کردن ارسال به سرور
        showJSToast(isFa ? 'عنوان تسک الزامی است.' : 'Task title is required.');
        ctTitle.focus();
        return;
      }
      if (titleVal.length > 100) {
        e.preventDefault(); // متوقف کردن ارسال به سرور
        showJSToast(isFa ? 'عنوان تسک نباید بیشتر از ۱۰۰ کاراکتر باشد.' : 'Title cannot exceed 100 characters.');
        ctTitle.focus();
        return;
      }
    }

    // ۲. بررسی توضیحات
    if (ctDesc) {
      const descVal = ctDesc.value.trim();
      if (descVal.length > 500) {
        e.preventDefault(); // متوقف کردن ارسال به سرور
        showJSToast(isFa ? 'توضیحات نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.' : 'Description cannot exceed 500 characters.');
        ctDesc.focus();
        return;
      }
    }

    // ۳. بررسی تاریخ
    const hiddenDate = document.getElementById('ct_expires_at_hidden');
    if (!hiddenDate || !hiddenDate.value) {
      e.preventDefault(); // متوقف کردن ارسال به سرور
      const msg = (window.I18N && window.I18N.js_alert_select_date) 
        ? window.I18N.js_alert_select_date 
        : 'Please select an expiry date.';
      showJSToast(msg);
      return;
    }
  });
}

// --- ▷ اعتبارسنجی فرم ویرایش تسک (Edit): Validate edit task form ---
const editForm = document.getElementById('editTaskForm');
if (editForm) {
  editForm.addEventListener('submit', function (e) {
    const hiddenDate = document.getElementById('et_expires_at_hidden');
    if (!hiddenDate || !hiddenDate.value) {
      e.preventDefault();
      const msg = (window.I18N && window.I18N.js_alert_select_date) 
        ? window.I18N.js_alert_select_date 
        : 'Please select an expiry date.';
      showJSToast(msg);
    }
  });
}

// ---------------------------------------------------------------------
// ⬛ MODAL HELPERS: Open and close logic
// ---------------------------------------------------------------------
function openModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.classList.remove('hidden');
  overlay.setAttribute('aria-hidden', 'false');
  const focusable = overlay.querySelector(
    'button:not([disabled]), input:not([readonly]):not([type="hidden"]), textarea:not([readonly]), select'
  );
  if (focusable) setTimeout(() => focusable.focus(), 50);
  document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.querySelectorAll('.jalali-cal:not(.hidden), .time-picker:not(.hidden)').forEach(p => {
    p.classList.add('hidden');
  });
  overlay.classList.add('hidden');
  overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

// Backdrop click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(overlay.id); });
});

// Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay:not(.hidden)').forEach(o => closeModal(o.id));
  }
});

// [data-modal] cancel/close buttons
document.querySelectorAll('[data-modal]').forEach(btn => {
  btn.addEventListener('click', () => closeModal(btn.getAttribute('data-modal')));
});

// ---------------------------------------------------------------------
// ⬛ CREATE MODAL: Open create modal and reset picker to today
// ---------------------------------------------------------------------
const openCreateBtn = document.getElementById('openCreateModalBtn');
if (openCreateBtn) {
  openCreateBtn.addEventListener('click', () => {
    // ریست کامل تاریخ و زمان بدون انتخاب پیش‌فرض تاریخ امروز
    if (createPicker) {
      createPicker._jy = null; createPicker._jm = null; createPicker._jd = null;
      createPicker._hh24 = null; createPicker._mm = null;
      if (createPicker.hiddenInput) createPicker.hiddenInput.value = '';
      if (createPicker.dateDisplay) createPicker.dateDisplay.textContent = (window.I18N && window.I18N.picker_select_date) ? window.I18N.picker_select_date : 'Select Date';
      if (createPicker.timeDisplay) createPicker.timeDisplay.textContent = (window.I18N && window.I18N.picker_select_time) ? window.I18N.picker_select_time : 'Select Time';
      createPicker._buildSummary();
    }
    if (createDurPicker) createDurPicker.reset();
    openModal('createTaskModal');
  });
}

// ---------------------------------------------------------------------
// ⬛ EDIT MODAL: Open edit modal and populate from data-* attributes
// ---------------------------------------------------------------------
document.querySelectorAll('[id^="editBtn-"]').forEach(btn => {
  btn.addEventListener('click', () => {
    const taskId    = btn.getAttribute('data-task-id');
    const title     = btn.getAttribute('data-title');
    const desc      = btn.getAttribute('data-description');
    const priority  = btn.getAttribute('data-priority');
    const expires   = btn.getAttribute('data-expires');   // Jalali YYYY-MM-DD
    const estimated = btn.getAttribute('data-estimated');

    // ۱. مقداردهی عنوان و توضیحات
    const titleEl = document.getElementById('et_title');
    const descEl  = document.getElementById('et_description');
    if (titleEl) titleEl.value = title || '';
    if (descEl)  descEl.value  = desc  || '';

    // ۲. مقداردهی اولویت (هم سلکت اصلی و هم سلکت سفارشی انیمیشنی)
    const priorityEl = document.getElementById('et_priority');
    if (priorityEl) {
      priorityEl.value = priority || '';
      priorityEl.dispatchEvent(new Event('change', { bubbles: true }));
      
      // آپدیت ظاهر سلکت کاستوم شیشه‌ای
      const wrapper = priorityEl.closest('.custom-select-wrapper');
      if (wrapper) {
        const triggerSpan = wrapper.querySelector('.custom-select-trigger span');
        const selectedOpt = priorityEl.options[priorityEl.selectedIndex];
        if (triggerSpan && selectedOpt) triggerSpan.textContent = selectedOpt.text;
        
        wrapper.querySelectorAll('.custom-select-option').forEach(optDiv => {
          optDiv.classList.toggle('selected', optDiv.textContent === (selectedOpt ? selectedOpt.text : ''));
        });
      }
    }

    // ۳. مقداردهی زمان تخمینی
    const estimatedEl = document.getElementById('et_estimated_time');
    if (editDurPicker) {
      if (estimated && estimated !== 'None') editDurPicker.prefill(estimated);
      else editDurPicker.reset();
    } else if (estimatedEl) {
      estimatedEl.value = (estimated && estimated !== 'None') ? estimated : '';
    }

    // ۴. مقداردهی دقیق تاریخ و زمان انقضای قبلی
    if (editPicker) {
      if (expires && expires !== 'None' && expires !== '') {
        // تبدیل اعداد فارسی به انگلیسی برای ساعت و تقویم
        const engExpires = String(expires).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
        
        const parts = engExpires.split(' ');
        const datePart = parts[0];
        const timePart = parts[1] || null;

        editPicker.prefill(datePart);

        if (timePart) {
          const [hh, mm] = timePart.split(':').map(Number);
          editPicker._hh24 = hh;
          editPicker._mm = mm;
          editPicker.time.setTime(hh, mm);
        } else {
          editPicker._hh24 = null;
          editPicker._mm = null;
        }
        editPicker._updateDisplay();
      } else {
        // اگر تاریخ قبلا خالی بوده، آن را کلا خالی نگه دار (تاریخ امروز را به زور وارد نکن)
        editPicker._jy = null; editPicker._jm = null; editPicker._jd = null;
        editPicker._hh24 = null; editPicker._mm = null;
        if (editPicker.hiddenInput) editPicker.hiddenInput.value = '';
        if (editPicker.dateDisplay) editPicker.dateDisplay.textContent = (window.I18N && window.I18N.picker_select_date) ? window.I18N.picker_select_date : 'Select Date';
        if (editPicker.timeDisplay) editPicker.timeDisplay.textContent = (window.I18N && window.I18N.picker_select_time) ? window.I18N.picker_select_time : 'Select Time';
        editPicker._buildSummary();
      }
    }

    const form = document.getElementById('editTaskForm');
    if (form) form.action = '/tasks/' + taskId + '/edit';

    openModal('editTaskModal');
  });
});

// ---------------------------------------------------------------------
// ⬛ MARK DONE: Async badge update (instant, before server round-trip)
// ---------------------------------------------------------------------
document.querySelectorAll('.done-form').forEach(form => {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const taskId = form.getAttribute('data-task-id');
    const badge  = document.getElementById('badge-' + taskId);

    // Instant DOM update — badge transitions to glass-green done state immediately
    if (badge) {
      badge.className = 'task-status-badge badge-done';
      badge.innerHTML = '<img src="/static/icons/check.svg" class="app-icon" alt="">';
    }

    // Swap button to disabled "Done" label instantly
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      const span = document.createElement('span');
      span.className = btn.className + ' btn-disabled';
      span.textContent = btn.textContent;
      form.replaceWith(span);
    }

    // POST to server, then follow redirect
    const fd = new FormData(form);
    fetch(form.action, { method: 'POST', body: fd, redirect: 'follow' })
      .then(r => { if (r.ok || r.redirected) window.location.replace(r.url || window.location.href); })
      .catch(() => window.location.reload());
  });
});

// ---------------------------------------------------------------------
// ⬛ DELETE CONFIRM: Translated string from window.I18N
// ---------------------------------------------------------------------
document.querySelectorAll('[id^="deleteBtn-"]').forEach(btn => {
  btn.addEventListener('click', () => {
    const formId = btn.getAttribute('data-form-id');
    const msg = (window.I18N && window.I18N.delete_confirm)
      ? window.I18N.delete_confirm
      : 'آیا مطمئن هستید که می‌خواهید این تسک را حذف کنید؟';
    
    const titleText = (window.USER_LANG_MAIN === 'fa' || document.documentElement.lang === 'fa') 
      ? 'حذف تسک' 
      : 'Delete Task';

    // استفاده از مودال کاستوم در صورت وجود، در غیر این‌صورت پیش‌فرض مرورگر
    if (window.showCustomConfirm) {
      window.showCustomConfirm(titleText, msg, () => {
        const form = document.getElementById(formId);
        if (form) form.submit();
      }, true); // true = نمایش دکمه تایید با استایل قرمز (btn-delete)
    } else {
      if (confirm(msg)) {
        const form = document.getElementById(formId);
        if (form) form.submit();
      }
    }
  });
});

// ---------------------------------------------------------------------
// ⬛ FILTER CUSTOM DATES: Show/hide custom date range groups
// ---------------------------------------------------------------------
const timeRangeFilter    = document.getElementById('timeRangeFilter');
const customDateGroup    = document.getElementById('customDateGroup');
const customDateGroupEnd = document.getElementById('customDateGroupEnd');

function updateCustomDateVisibility(sel, gs, ge) {
  if (!sel) return;
  const isCustom = sel.value === 'custom';
  if (gs) gs.classList.toggle('hidden', !isCustom);
  if (ge) ge.classList.toggle('hidden', !isCustom);
}

if (timeRangeFilter) {
  timeRangeFilter.addEventListener('change', () =>
    updateCustomDateVisibility(timeRangeFilter, customDateGroup, customDateGroupEnd));
  updateCustomDateVisibility(timeRangeFilter, customDateGroup, customDateGroupEnd);
}

const aTimeRange          = document.getElementById('a_time_range');
const aCustomDateGroup    = document.getElementById('aCustomDateGroup');
const aCustomDateGroupEnd = document.getElementById('aCustomDateGroupEnd');

if (aTimeRange) {
  aTimeRange.addEventListener('change', () =>
    updateCustomDateVisibility(aTimeRange, aCustomDateGroup, aCustomDateGroupEnd));
  updateCustomDateVisibility(aTimeRange, aCustomDateGroup, aCustomDateGroupEnd);
}



// ---------------------------------------------------------------------
// ⬛ LIVE SEARCH: Instant Filter by Title
// ---------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('taskLiveSearch');
  const taskCards = document.querySelectorAll('.task-card');
  const countBadge = document.getElementById('taskCountBadge');
  const clearBtn = document.getElementById('clearSearchBtn'); // دکمه ضربدر

  if (searchInput) {
    // یک تابع واحد برای بررسی وضعیت جستجو
    function filterTasks() {
      const searchTerm = searchInput.value.toLowerCase().trim();
      let visibleCount = 0;

      // نمایش یا مخفی کردن دکمه ضربدر بر اساس طول متن
      if (clearBtn) {
        clearBtn.style.display = searchTerm.length > 0 ? 'block' : 'none';
      }

      // فیلتر کردن کارت‌ها
      taskCards.forEach(card => {
        const titleElement = card.querySelector('.task-title');
        if (titleElement) {
          const title = titleElement.textContent.toLowerCase();
          if (title.includes(searchTerm)) {
            card.style.display = '';
            visibleCount++;
          } else {
            card.style.display = 'none';
          }
        }
      });

      // آپدیت کردن عدد بج (شمارنده تسک‌ها)
      if (countBadge) {
        countBadge.textContent = visibleCount;
      }
    }

    // وقتی کاربر تایپ می‌کند، فیلتر را اجرا کن
    searchInput.addEventListener('input', filterTasks);

    // وقتی کاربر روی دکمه ضربدر کلیک می‌کند
    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        searchInput.value = ''; // خالی کردن متن باکس
        filterTasks(); // اجرای مجدد فیلتر تا لیست کامل تسک‌ها برگردد
        searchInput.focus(); // برگرداندن نشانگر موس به داخل باکس برای راحتی بیشتر کاربر
      });
    }
  }

// ---------------------------------------------------------------------
// ⬛ CUSTOM SELECT DROPDOWNS: Auto-Converter for native selects
// ---------------------------------------------------------------------
const nativeSelects = document.querySelectorAll('select.filter-select, select.form-control');

nativeSelects.forEach(select => {
  // ۱. ساخت کانتینر اصلی
  const wrapper = document.createElement('div');
  wrapper.className = 'custom-select-wrapper';
  select.parentNode.insertBefore(wrapper, select);
  wrapper.appendChild(select); // انتقال سلکت اصلی به داخل کانتینر
  
  // ۲. ساخت دکمه‌ای که کاربر می‌بیند
  const trigger = document.createElement('div');
  trigger.className = 'custom-select-trigger';
  const selectedOpt = select.options[select.selectedIndex];
  
  // بررسی وجود آیکون برای این سلکت باکس
  const iconSrc = select.getAttribute('data-icon');
  let iconHtml = '';
  if (iconSrc) {
    iconHtml = `<img src="${iconSrc}" class="app-icon" style="margin-inline-end: 0.4rem;" alt="">`;
  }
  
  trigger.innerHTML = `<div style="display: flex; align-items: center;">${iconHtml}<span>${selectedOpt ? selectedOpt.text : ''}</span></div>`;
  wrapper.appendChild(trigger);
  
  // ۳. ساخت لیست منو
  const optionsList = document.createElement('div');
  optionsList.className = 'custom-select-options';
  wrapper.appendChild(optionsList);
  
  // ۴. کپی کردن گزینه‌ها از سلکت اصلی به منوی جدید
  Array.from(select.options).forEach(option => {
    const optDiv = document.createElement('div');
    optDiv.className = 'custom-select-option';
    optDiv.textContent = option.text;
    if(option.selected) optDiv.classList.add('selected');
    
    // وقتی کاربر روی گزینه کاستوم کلیک می‌کند
    optDiv.addEventListener('click', function(e) {
      e.stopPropagation();
      
      // مقدار سلکت اصلی را آپدیت کن
      select.value = option.value;
      trigger.querySelector('span').textContent = option.text;
      
      // رنگ گزینه انتخاب شده را آپدیت کن
      optionsList.querySelectorAll('.custom-select-option').forEach(el => el.classList.remove('selected'));
      optDiv.classList.add('selected');
      
      // منو را ببند
      wrapper.classList.remove('open');
      
      // به فرم‌ها اطلاع بده که مقدار تغییر کرده است
      select.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    optionsList.appendChild(optDiv);
  });
  
  // باز و بسته شدن با کلیک
  trigger.addEventListener('click', function(e) {
    e.stopPropagation();
    // ابتدا بقیه منوهای باز را ببند
    document.querySelectorAll('.custom-select-wrapper').forEach(w => {
      if(w !== wrapper) w.classList.remove('open');
    });
    // حالا این منو را باز/بسته کن
    wrapper.classList.toggle('open');
  });
});

// کلیک بیرون از منو باعث بسته شدن آن می‌شود
document.addEventListener('click', function() {
  document.querySelectorAll('.custom-select-wrapper').forEach(w => w.classList.remove('open'));
});

});


// ---------------------------------------------------------------------
// ⬛ PWA SMART BANNER: App Pages - 30s Delay, Session Memory
// ---------------------------------------------------------------------
let deferredPrompt;
const pwaInstallBanner = document.getElementById('pwaInstallBanner');
const pwaInstallBtn = document.getElementById('pwaInstallBtn');
const pwaCloseBtn = document.getElementById('pwaCloseBtn');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;

  if (pwaInstallBanner) {
    // اگر کاربر در این نشست (پس از لاگین) بنر را قبلاً بسته است، متوقف شو
    if (sessionStorage.getItem('pwaClosedInSession') === 'true') {
      return;
    }

    // تنظیم تایمر روی ۳۰ ثانیه برای داشبورد کاربری
    setTimeout(() => {
      if (deferredPrompt) {
        pwaInstallBanner.classList.add('show');
      }
    }, 30000); 
  }
});

if (pwaInstallBtn) {
  pwaInstallBtn.addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;
      pwaInstallBanner.classList.remove('show');
    }
  });
}

if (pwaCloseBtn) {
  pwaCloseBtn.addEventListener('click', () => {
    pwaInstallBanner.classList.remove('show');
    // ثبت در حافظه: بنر بسته شد و تا لاگ‌اوت بعدی کاربر، دیگر مزاحمش نشو
    sessionStorage.setItem('pwaClosedInSession', 'true');
  });
}

window.addEventListener('appinstalled', () => {
  if (pwaInstallBanner) pwaInstallBanner.classList.remove('show');
  deferredPrompt = null;
});
