/**
 * landing.js — Page-scoped JS for the public landing page.
 * Only responsibility: FAQ accordion toggle.
 * Does not touch any global state, auth, or translation logic.
 */
'use strict';

// =====================================================================
// FILE: static/js/landing.js
// PURPOSE: Page-scoped interactivity for the public landing page. Handles FAQ accordion toggle behavior with single-open constraint.
// =====================================================================

// ---------------------------------------------------------------------
// FAQ ACCORDION: Single-open toggle behavior for question items
// ---------------------------------------------------------------------
document.querySelectorAll('.lp-faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const item     = btn.closest('.lp-faq-item');
    const isOpen   = item.classList.contains('open');

    // Close all items first (single-open accordion)
    document.querySelectorAll('.lp-faq-item').forEach(el => {
      el.classList.remove('open');
      el.querySelector('.lp-faq-q').setAttribute('aria-expanded', 'false');
    });

    // Toggle clicked item if it wasn't already open
    if (!isOpen) {
      item.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
    }
  });
});


// ---------------------------------------------------------------------
// PWA SMART BANNER: Landing Page - 30s Delay, Auto-Reprompt
// ---------------------------------------------------------------------
let deferredPrompt;
const pwaInstallBanner = document.getElementById('pwaInstallBanner');
const pwaInstallBtn = document.getElementById('pwaInstallBtn');
const pwaCloseBtn = document.getElementById('pwaCloseBtn');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  if (pwaInstallBanner) {
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
  });
}

window.addEventListener('appinstalled', () => {
  if (pwaInstallBanner) pwaInstallBanner.classList.remove('show');
  deferredPrompt = null;
});