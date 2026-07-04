/* Calculators.Finance — Ad & consent configuration.
   Fill these in after AdSense approval. Leave publisherId blank to keep the
   CMP, Consent Mode, and every ad slot fully inactive (safe default pre-approval). */
window.__ADS_CONFIG__ = {
  // Numeric AdSense publisher id only — e.g. "3649044515825371" (no "ca-pub-"/"pub-" prefix)
  publisherId: "",

  // One AdSense ad unit slot id per placement. Create these in the AdSense
  // dashboard after approval, then paste each numeric slot id below.
  slots: {
    belowResult: "",
    inContent: "",
    sidebar: "",
    mobileAnchor: ""
  },

  // Flip any placement off site-wide without touching page markup.
  placements: {
    belowResult: true,
    inContent: true,
    sidebar: true,
    mobileAnchor: true
  }
};
