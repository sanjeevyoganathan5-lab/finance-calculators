/* Calculators.Finance — Consent Mode v2 bootstrap.
   Loads before any advertising tag. Requires ads-config.js to load first.
   Sets Consent Mode defaults to "denied", then wires up whichever
   Google-certified CMP is configured (Funding Choices by default) and
   listens for the IAB TCF v2 signal every certified CMP exposes, so this
   works unchanged if the publisher swaps in Cookiebot or CookieYes instead. */
(function () {
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // Deny ad/analytics storage until the CMP reports an actual decision.
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500
  });

  window.__consentGranted = false;

  function broadcast(granted) {
    if (window.__consentGranted === granted) return;
    window.__consentGranted = granted;
    document.dispatchEvent(new CustomEvent('cf:consent-change', { detail: { granted: granted } }));
  }

  var cfg = window.__ADS_CONFIG__ || {};
  var pubId = cfg.publisherId;

  // No AdSense account configured yet (pre-approval) — stay denied, load no CMP/ad script.
  if (!pubId) return;

  // Google's own free CMP (Privacy & messaging / Funding Choices), tied to the AdSense account.
  var fc = document.createElement('script');
  fc.async = true;
  fc.src = 'https://fundingchoicesmessages.google.com/i/pub-' + pubId + '?ers=1';
  document.head.appendChild(fc);

  (function signalGooglefcPresent() {
    if (!window.frames['googlefcPresent']) {
      if (document.body) {
        var iframe = document.createElement('iframe');
        iframe.style.cssText = 'width:0;height:0;border:none;z-index:-1000;left:-1000px;top:-1000px;position:absolute;';
        iframe.name = 'googlefcPresent';
        document.body.appendChild(iframe);
      } else {
        setTimeout(signalGooglefcPresent, 0);
      }
    }
  })();

  // Every Google-certified CMP implements the IAB TCF v2 API — read consent
  // there so this is not tied to Funding Choices specifically.
  function readTCF() {
    if (typeof window.__tcfapi !== 'function') return false;
    window.__tcfapi('addEventListener', 2, function (tcData, success) {
      if (!success || !tcData) return;
      if (tcData.eventStatus === 'tcloaded' || tcData.eventStatus === 'useractioncomplete') {
        // Purpose 1 = "store and/or access information on a device" — the
        // baseline consent needed before any ad cookie may be set.
        var purposeConsents = (tcData.purpose && tcData.purpose.consent) || {};
        var granted = tcData.gdprApplies === false ? true : !!purposeConsents['1'];
        gtag('consent', 'update', {
          ad_storage: granted ? 'granted' : 'denied',
          ad_user_data: granted ? 'granted' : 'denied',
          ad_personalization: granted ? 'granted' : 'denied',
          analytics_storage: granted ? 'granted' : 'denied'
        });
        broadcast(granted);
      }
    });
    return true;
  }

  var attempts = 0;
  var poll = setInterval(function () {
    attempts++;
    if (readTCF() || attempts > 150) clearInterval(poll); // ~30s for the CMP to attach
  }, 200);

  // Any element with data-consent-manage re-opens the CMP's preference UI.
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-consent-manage]');
    if (!el) return;
    e.preventDefault();
    if (window.googlefc && window.googlefc.showRevocationMessage) {
      window.googlefc.showRevocationMessage();
    }
  });
})();
