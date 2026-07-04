/* Calculators.Finance — reusable ad-slot component.
   Requires ads-config.js + consent.js to load first.
   - Loads adsbygoogle.js only after consent is granted (never before).
   - Lazy-inits each .ad-slot only once it nears the viewport.
   - Never double-pushes the same slot.
   - Each placement can be disabled via ads-config.js without touching markup. */
(function () {
  var cfg = window.__ADS_CONFIG__ || {};
  var placements = cfg.placements || {};
  var slots = cfg.slots || {};
  var clientId = cfg.publisherId ? ('ca-pub-' + cfg.publisherId) : '';

  if (!clientId) return; // no AdSense account configured yet — render nothing

  function toCamel(kebab) {
    return (kebab || '').replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); });
  }

  function slotEnabled(el) {
    var placement = toCamel(el.getAttribute('data-placement'));
    return placements[placement] !== false;
  }

  var adsenseRequested = false;
  function loadAdsenseScript() {
    if (adsenseRequested || document.getElementById('adsbygoogle-js')) return;
    adsenseRequested = true;
    var s = document.createElement('script');
    s.id = 'adsbygoogle-js';
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + clientId;
    document.head.appendChild(s);
  }

  function initSlot(el) {
    if (el.dataset.cfInit) return;
    var placement = toCamel(el.getAttribute('data-placement'));
    var slotId = slots[placement];
    if (!slotId) return; // no ad unit id configured for this placement yet
    el.dataset.cfInit = '1';

    var ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    ins.style.display = 'block';
    ins.setAttribute('data-ad-client', clientId);
    ins.setAttribute('data-ad-slot', slotId);
    if (el.hasAttribute('data-ad-format')) {
      ins.setAttribute('data-ad-format', el.getAttribute('data-ad-format'));
    }
    if (el.hasAttribute('data-full-width-responsive')) {
      ins.setAttribute('data-full-width-responsive', el.getAttribute('data-full-width-responsive'));
    }
    el.appendChild(ins);

    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }

  var observer = null;
  function observeSlots() {
    var els = document.querySelectorAll('.ad-slot');
    els.forEach(function (el) {
      if (el.dataset.cfInit || !slotEnabled(el)) return;
      if (el.getAttribute('data-placement') === 'mobile-anchor') return; // handled separately
      if (!observer) {
        observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              initSlot(entry.target);
              observer.unobserve(entry.target);
            }
          });
        }, { rootMargin: '200px 0px' });
      }
      observer.observe(el);
    });
  }

  function initMobileAnchor() {
    var el = document.querySelector('.ad-slot[data-placement="mobile-anchor"]');
    if (!el || !slotEnabled(el)) return;
    if (window.matchMedia && !window.matchMedia('(max-width: 760px)').matches) return;
    if (sessionStorage.getItem('cf-anchor-dismissed') === '1') return;

    el.classList.add('ad-anchor-visible');
    document.body.classList.add('has-ad-anchor');

    var closeBtn = el.querySelector('.ad-anchor-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        el.classList.remove('ad-anchor-visible');
        document.body.classList.remove('has-ad-anchor');
        sessionStorage.setItem('cf-anchor-dismissed', '1');
      });
    }
    initSlot(el);
  }

  function onConsentGranted() {
    loadAdsenseScript();
    observeSlots();
    initMobileAnchor();
  }

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    if (window.__consentGranted) onConsentGranted();
    document.addEventListener('cf:consent-change', function (e) {
      if (e.detail.granted) onConsentGranted();
    });
  });
})();
