'use strict';
/**
 * analytics.js — Chart.js donut charts for the analytics page.
 *
 * Rules enforced:
 *   - Chart.js is ONLY instantiated when total > 0.
 *   - If total = 0, a grey solid circle is drawn via raw Canvas 2D API
 *     with the message "هیچ تسکی وجود ندارد".
 *   - Colors match the CSS custom properties:
 *       pending  → #0ea5e9
 *       done     → #10b981
 *       expired  → #ef4444
 *
 * Data is passed from the template via window.ANALYTICS_DATA.
 */

// =====================================================================
// FILE: static/js/analytics.js
// PURPOSE: Client-side engine for the PlanSpark Analytics dashboard. Renders Chart.js donut charts, computes visual statistics, and handles date-range filtering.
// =====================================================================

// ---------------------------------------------------------------------
// CHART CONSTANTS: Color palette matching CSS custom properties
// ---------------------------------------------------------------------
// Color constants (match CSS :root variables)
const COLORS = {
  pending: '#0ea5e9',
  done:    '#10b981',
  expired: '#ef4444',
  empty:   '#cbd5e1',
};

/**
 * Render a Chart.js donut chart on the given canvas element.
 *
 * @param {HTMLCanvasElement} canvas - Target canvas
 * @param {number} pending  - Pending count
 * @param {number} done     - Done count
 * @param {number} expired  - Expired count
 */
function renderDonut(canvas, pending, done, expired) {
  if (!canvas) return;

  const total = pending + done + expired;
  if (total === 0) return;

  // Use translated labels from template if available
  const labels = window.CHART_LABELS || { pending: 'در انتظار', done: 'انجام شده', expired: 'منقضی' };
  const tasksUnit = (window.CHART_LABELS ? '' : ' تسک');

  new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: [labels.pending, labels.done, labels.expired],
      datasets: [{
        data: [pending, done, expired],
        backgroundColor: [COLORS.pending, COLORS.done, COLORS.expired],
        borderColor: 'transparent',
        borderWidth: 0,
        hoverOffset: 8,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: false,
      cutout: '68%',
      animation: { animateRotate: true, duration: 800, easing: 'easeInOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          rtl: document.documentElement.dir === 'rtl',
          bodyFont: { family: 'Vazirmatn, Inter, sans-serif', size: 13 },
          callbacks: {
            label: function (ctx) {
              const value = ctx.parsed;
              const pct = total > 0 ? Math.round((value / total) * 100) : 0;
              return ` ${value} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

/**
 * Draw a solid grey circle with a center label on a canvas
 * when total = 0. Does NOT use Chart.js.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {string} message - Persian text to display
 */
function renderEmptyCircle(canvas, message) {
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const radius = Math.min(w, h) / 2 - 6;

  // Draw outer grey circle
  ctx.clearRect(0, 0, w, h);
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.fillStyle = COLORS.empty;
  ctx.fill();

  // Inner donut hole
  ctx.beginPath();
  ctx.arc(cx, cy, radius * 0.68, 0, Math.PI * 2);
  ctx.fillStyle = getComputedCanvasBg(canvas);
  ctx.fill();

  // Draw text label in center
  ctx.fillStyle = '#94a3b8';
  ctx.font = 'bold 11px Vazirmatn, Tahoma, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  // Word-wrap: split into max 2 lines
  const words = message.split(' ');
  if (words.length <= 2) {
    ctx.fillText(message, cx, cy);
  } else {
    const mid = Math.ceil(words.length / 2);
    const line1 = words.slice(0, mid).join(' ');
    const line2 = words.slice(mid).join(' ');
    ctx.fillText(line1, cx, cy - 8);
    ctx.fillText(line2, cx, cy + 8);
  }
}

/**
 * Detect the canvas background colour from body dark class.
 * Returns a colour string for the donut hole.
 */
function getComputedCanvasBg(canvas) {
  if (document.body.classList.contains('dark')) {
    return 'rgba(15, 10, 30, 0.75)';
  }
  return 'rgba(255, 255, 255, 0.72)';
}

// ---------------------------------------------------------------------
// INITIALIZATION: Data loading and chart rendering on page load
// ---------------------------------------------------------------------
(function initCharts() {
  const data = window.ANALYTICS_DATA;
  if (!data) return;

  const labels = window.CHART_LABELS || {
    pending: 'در انتظار',
    done: 'انجام شده',
    expired: 'منقضی',
  };
  const noTasks       = labels.analytics_no_tasks      || 'هیچ تسکی وجود ندارد';
  const noTasksRange  = labels.analytics_no_tasks_range || 'هیچ تسکی در این بازه وجود ندارد';

  // Box 1
  const box1Canvas      = document.getElementById('box1Chart');
  const box1EmptyCanvas = document.getElementById('box1EmptyCanvas');
  if (data.box1.total > 0 && box1Canvas) {
    renderDonut(box1Canvas, data.box1.pending, data.box1.done, data.box1.expired);
  } else if (box1EmptyCanvas) {
    renderEmptyCircle(box1EmptyCanvas, noTasks);
  }

  // Box 2
  const box2Canvas      = document.getElementById('box2Chart');
  const box2EmptyCanvas = document.getElementById('box2EmptyCanvas');
  if (data.box2.total > 0 && box2Canvas) {
    renderDonut(box2Canvas, data.box2.pending, data.box2.done, data.box2.expired);
  } else if (box2EmptyCanvas) {
    renderEmptyCircle(box2EmptyCanvas, noTasksRange);
  }
})();

// ---------------------------------------------------------------------
// ANALYTICS FILTER: Custom date range visibility
// ---------------------------------------------------------------------
(function initAnalyticsFilter() {
  const timeRangeSelect    = document.getElementById('a_time_range');
  const customGroupStart   = document.getElementById('aCustomDateGroup');
  const customGroupEnd     = document.getElementById('aCustomDateGroupEnd');

  function toggleCustomDates() {
    if (!timeRangeSelect) return;
    const isCustom = timeRangeSelect.value === 'custom';
    if (customGroupStart) customGroupStart.classList.toggle('hidden', !isCustom);
    if (customGroupEnd)   customGroupEnd.classList.toggle('hidden', !isCustom);
  }

  if (timeRangeSelect) {
    timeRangeSelect.addEventListener('change', toggleCustomDates);
    toggleCustomDates(); // on load
  }
})();
