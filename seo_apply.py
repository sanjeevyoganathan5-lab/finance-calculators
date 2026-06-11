#!/usr/bin/env python3
"""
seo_apply.py — Full SEO & E-E-A-T improvements for calculators.finance
Run once from the calculators-updated directory.

Sections handled:
  1. lang="en" → lang="en-GB" on all pages
  2. fonts.gstatic.com preconnect on all pages
  3. Organization schema on all pages
  4. OG image meta tags (category-specific)
  5. WebApplication schema: add author/reviewedBy/dateModified
  6. Article schema (guides): update author to named Person
  7. BreadcrumbList schema on calculators and guides
  8. WebSite schema with SearchAction on index
  9. Author byline block (all calc/guide/index pages)
 10. Related-calculators block (calculator pages only)
"""

import re
import json
from pathlib import Path

BASE = Path(__file__).parent

# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────

SITE_URL    = "https://calculators.finance"
SITE_NAME   = "Calculators.Finance"
AUTHOR_ID   = "https://calculators.finance/about#author"
AUTHOR_NAME = "Sanjeev Yoganathan"
LINKEDIN    = "https://www.linkedin.com/in/sanjeev-yoganathan-08156492/"
AUTHOR_CRED = "BSc Actuarial Science · 10+ years in insurance, pricing and financial services"

PERSON_REF = {"@type": "Person", "@id": AUTHOR_ID, "name": AUTHOR_NAME}

# ─────────────────────────────────────────────────────────────────
# Calculator metadata
# ─────────────────────────────────────────────────────────────────

CALCS = {
    "take-home-pay-calculator": {
        "name": "UK Take-Home Pay Calculator",
        "cat": "tax", "og": "og-tax.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("salary-sacrifice-calculator",    "Salary Sacrifice Calculator"),
            ("pension-contribution-calculator", "Pension Contribution Calculator"),
            ("salary-to-hourly-calculator",    "Salary to Hourly Calculator"),
        ],
    },
    "salary-sacrifice-calculator": {
        "name": "UK Salary Sacrifice Calculator",
        "cat": "tax", "og": "og-tax.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("take-home-pay-calculator",        "Take-Home Pay Calculator"),
            ("pension-contribution-calculator", "Pension Contribution Calculator"),
            ("salary-to-hourly-calculator",     "Salary to Hourly Calculator"),
        ],
    },
    "salary-to-hourly-calculator": {
        "name": "Salary to Hourly Calculator",
        "cat": "tax", "og": "og-tax.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("take-home-pay-calculator",    "Take-Home Pay Calculator"),
            ("freelance-rate-calculator",   "Freelance Rate Calculator"),
            ("vat-calculator",              "VAT Calculator"),
        ],
    },
    "vat-calculator": {
        "name": "UK VAT Calculator",
        "cat": "tax", "og": "og-tax.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("freelance-rate-calculator",   "Freelance Rate Calculator"),
            ("break-even-calculator",       "Break-Even Calculator"),
            ("salary-to-hourly-calculator", "Salary to Hourly Calculator"),
        ],
    },
    "pension-contribution-calculator": {
        "name": "UK Pension Contribution Calculator",
        "cat": "tax", "og": "og-tax.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("take-home-pay-calculator",    "Take-Home Pay Calculator"),
            ("salary-sacrifice-calculator", "Salary Sacrifice Calculator"),
            ("isa-vs-pension-calculator",   "ISA vs Pension Calculator"),
        ],
    },
    "stamp-duty-calculator": {
        "name": "UK Stamp Duty Calculator",
        "cat": "property", "og": "og-property.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("mortgage-affordability-calculator", "Mortgage Affordability Calculator"),
            ("rent-vs-buy-calculator",            "Rent vs Buy Calculator"),
        ],
    },
    "mortgage-affordability-calculator": {
        "name": "UK Mortgage Affordability Calculator",
        "cat": "property", "og": "og-property.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("stamp-duty-calculator",  "Stamp Duty Calculator"),
            ("rent-vs-buy-calculator", "Rent vs Buy Calculator"),
        ],
    },
    "rent-vs-buy-calculator": {
        "name": "UK Rent vs Buy Calculator",
        "cat": "property", "og": "og-property.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("mortgage-affordability-calculator", "Mortgage Affordability Calculator"),
            ("stamp-duty-calculator",             "Stamp Duty Calculator"),
        ],
    },
    "compound-interest-calculator": {
        "name": "Compound Interest Calculator",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("savings-goal-calculator",      "Savings Goal Calculator"),
            ("inflation-calculator",         "Inflation Calculator"),
            ("investment-return-calculator", "Investment Return Calculator"),
        ],
    },
    "savings-goal-calculator": {
        "name": "Savings Goal Calculator",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("compound-interest-calculator", "Compound Interest Calculator"),
            ("emergency-fund-calculator",    "Emergency Fund Calculator"),
            ("budget-planner",               "Budget Planner"),
        ],
    },
    "emergency-fund-calculator": {
        "name": "Emergency Fund Calculator",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("savings-goal-calculator",      "Savings Goal Calculator"),
            ("budget-planner",               "Budget Planner"),
            ("compound-interest-calculator", "Compound Interest Calculator"),
        ],
    },
    "budget-planner": {
        "name": "Monthly Budget Planner",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("emergency-fund-calculator", "Emergency Fund Calculator"),
            ("savings-goal-calculator",   "Savings Goal Calculator"),
            ("net-worth-calculator",      "Net Worth Calculator"),
        ],
    },
    "inflation-calculator": {
        "name": "UK Inflation Calculator",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("compound-interest-calculator", "Compound Interest Calculator"),
            ("investment-return-calculator", "Investment Return Calculator"),
            ("savings-goal-calculator",      "Savings Goal Calculator"),
        ],
    },
    "net-worth-calculator": {
        "name": "Net Worth Calculator",
        "cat": "savings", "og": "og-savings.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("budget-planner",               "Budget Planner"),
            ("investment-return-calculator", "Investment Return Calculator"),
            ("fire-calculator",              "FIRE Calculator"),
        ],
    },
    "loan-repayment-calculator": {
        "name": "Loan Repayment Calculator",
        "cat": "debt", "og": "og-debt.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("credit-card-payoff-calculator", "Credit Card Payoff Calculator"),
            ("debt-snowball-calculator",       "Debt Snowball Calculator"),
        ],
    },
    "credit-card-payoff-calculator": {
        "name": "Credit Card Payoff Calculator",
        "cat": "debt", "og": "og-debt.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("loan-repayment-calculator", "Loan Repayment Calculator"),
            ("debt-snowball-calculator",  "Debt Snowball Calculator"),
        ],
    },
    "debt-snowball-calculator": {
        "name": "Debt Snowball Calculator",
        "cat": "debt", "og": "og-debt.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("loan-repayment-calculator",     "Loan Repayment Calculator"),
            ("credit-card-payoff-calculator", "Credit Card Payoff Calculator"),
        ],
    },
    "investment-return-calculator": {
        "name": "Investment Return Calculator",
        "cat": "investing", "og": "og-investing.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("fire-calculator",          "FIRE Calculator"),
            ("isa-vs-pension-calculator","ISA vs Pension Calculator"),
            ("compound-interest-calculator","Compound Interest Calculator"),
        ],
    },
    "fire-calculator": {
        "name": "FIRE Calculator",
        "cat": "investing", "og": "og-investing.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("investment-return-calculator",   "Investment Return Calculator"),
            ("isa-vs-pension-calculator",      "ISA vs Pension Calculator"),
            ("pension-contribution-calculator","Pension Contribution Calculator"),
        ],
    },
    "isa-vs-pension-calculator": {
        "name": "ISA vs Pension Calculator",
        "cat": "investing", "og": "og-investing.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("fire-calculator",               "FIRE Calculator"),
            ("investment-return-calculator",  "Investment Return Calculator"),
            ("pension-contribution-calculator","Pension Contribution Calculator"),
        ],
    },
    "currency-converter": {
        "name": "Currency Converter",
        "cat": "investing", "og": "og-investing.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("investment-return-calculator", "Investment Return Calculator"),
            ("inflation-calculator",         "Inflation Calculator"),
        ],
    },
    "break-even-calculator": {
        "name": "Break-Even Calculator",
        "cat": "business", "og": "og-business.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("freelance-rate-calculator", "Freelance Rate Calculator"),
            ("vat-calculator",            "VAT Calculator"),
        ],
    },
    "freelance-rate-calculator": {
        "name": "Freelance Rate Calculator",
        "cat": "business", "og": "og-business.svg",
        "dateModified": "2025-04-06",
        "related": [
            ("break-even-calculator",       "Break-Even Calculator"),
            ("vat-calculator",              "VAT Calculator"),
            ("salary-to-hourly-calculator", "Salary to Hourly Calculator"),
        ],
    },
}

GUIDES_META = {
    "how-much-tax-will-i-pay":        {"og": "og-tax.svg"},
    "stamp-duty-explained":           {"og": "og-property.svg"},
    "how-much-can-i-borrow-mortgage": {"og": "og-property.svg"},
    "isa-vs-pension":                 {"og": "og-investing.svg"},
    "what-is-fire-movement":          {"og": "og-investing.svg"},
    "guides":                         {"og": "og-home.svg"},
}

CAT_COLORS = {
    "tax":      "#2563eb",
    "property": "#0891b2",
    "savings":  "#16a34a",
    "debt":     "#dc2626",
    "investing":"#7c3aed",
    "business": "#d97706",
}

# ─────────────────────────────────────────────────────────────────
# Schema helpers
# ─────────────────────────────────────────────────────────────────

ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": SITE_NAME,
    "url": SITE_URL,
    "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/favicon.svg"},
    "sameAs": [LINKEDIN],
}

WEBSITE_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": SITE_NAME,
    "url": SITE_URL,
    "description": "23 free UK finance calculators built on HMRC 2025/26 published rates.",
    "potentialAction": {
        "@type": "SearchAction",
        "target": {"@type": "EntryPoint", "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}"},
        "query-input": "required name=search_term_string",
    },
}


def schema_tag(obj):
    return f'<script type="application/ld+json">\n{json.dumps(obj, indent=2, ensure_ascii=False)}\n</script>'


def breadcrumb_for_calc(slug):
    name = CALCS[slug]["name"]
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",         "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Calculators",  "item": SITE_URL},
            {"@type": "ListItem", "position": 3, "name": name,           "item": f"{SITE_URL}/{slug}"},
        ],
    }


def breadcrumb_for_guide(slug, title):
    if slug == "guides":
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home",   "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE_URL}/guides"},
            ],
        }
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",   "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE_URL}/guides"},
            {"@type": "ListItem", "position": 3, "name": title,    "item": f"{SITE_URL}/{slug}"},
        ],
    }


# ─────────────────────────────────────────────────────────────────
# HTML blocks
# ─────────────────────────────────────────────────────────────────

def author_byline_html(max_w="820px"):
    return (
        f'\n<div style="font-family:\'Inter\',sans-serif;max-width:{max_w};'
        'margin:0 auto;padding:0 20px 28px;">\n'
        '  <div style="display:flex;align-items:center;gap:12px;background:#fff;'
        'border:1px solid #e2e8f0;border-radius:8px;padding:16px 20px;">\n'
        '    <div style="width:40px;height:40px;min-width:40px;background:#2563eb;'
        'border-radius:50%;display:flex;align-items:center;justify-content:center;'
        'color:#fff;font-weight:700;font-size:14px;">SY</div>\n'
        '    <div>\n'
        '      <div style="font-size:13px;font-weight:600;color:#0f172a;">Written and reviewed by '
        '<a href="/about" style="color:#2563eb;text-decoration:none;">Sanjeev Yoganathan</a></div>\n'
        f'      <div style="font-size:12px;color:#64748b;margin-top:3px;">{AUTHOR_CRED}</div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
    )


def related_calcs_html(slug, max_w="820px"):
    meta = CALCS.get(slug)
    if not meta:
        return ""
    color = CAT_COLORS.get(meta["cat"], "#2563eb")
    links = "\n      ".join(
        f'<a href="/{s}" style="display:inline-flex;align-items:center;gap:4px;'
        f'background:{color}14;color:{color};border:1px solid {color}33;'
        f'border-radius:6px;padding:8px 14px;font-size:13px;font-weight:500;'
        f'text-decoration:none;white-space:nowrap;">{n} →</a>'
        for s, n in meta["related"]
    )
    return (
        f'\n<div style="font-family:\'Inter\',sans-serif;max-width:{max_w};'
        'margin:0 auto;padding:0 20px 8px;">\n'
        '  <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;'
        'padding:20px 24px;">\n'
        '    <div style="font-size:11px;font-weight:600;letter-spacing:.08em;'
        'text-transform:uppercase;color:#64748b;margin-bottom:12px;">Related Calculators</div>\n'
        '    <div style="display:flex;flex-wrap:wrap;gap:8px;">\n'
        f'      {links}\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
    )


# ─────────────────────────────────────────────────────────────────
# Core processing
# ─────────────────────────────────────────────────────────────────

LDRE = re.compile(
    r'<script\s+type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
    re.IGNORECASE,
)


def process_file(path: Path, slug: str, *,
                 is_calc=False, is_guide=False, is_index=False):
    txt = path.read_text(encoding="utf-8")
    original = txt

    # 1. lang="en" → lang="en-GB"
    txt = re.sub(r'<html\s+lang="en"', '<html lang="en-GB"', txt, count=1)

    # 2. fonts.gstatic.com preconnect (idempotent)
    if "fonts.gstatic.com" not in txt:
        txt = txt.replace(
            '<link rel="preconnect" href="https://fonts.googleapis.com" />',
            '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
            1,
        )

    # 3. Organization schema (idempotent)
    if '"Organization"' not in txt:
        txt = txt.replace("</head>", schema_tag(ORG_SCHEMA) + "\n</head>", 1)

    # 4. OG image tags (idempotent)
    if 'og:image' not in txt:
        if is_calc:
            og_url = f"{SITE_URL}/{CALCS[slug]['og']}"
        elif is_guide:
            og_url = f"{SITE_URL}/{GUIDES_META[slug]['og']}"
        elif is_index:
            og_url = f"{SITE_URL}/og-home.svg"
        else:
            og_url = None
        if og_url:
            og_block = (
                f'  <meta property="og:image" content="{og_url}" />\n'
                f'  <meta property="og:image:width" content="1200" />\n'
                f'  <meta property="og:image:height" content="630" />\n'
                f'  <meta name="twitter:image" content="{og_url}" />'
            )
            # Insert after og:site_name if present, else before </head>
            if 'og:site_name' in txt:
                txt = re.sub(
                    r'(<meta property="og:site_name"[^>]*/?>)',
                    r'\1\n' + og_block,
                    txt, count=1,
                )
            else:
                txt = txt.replace("</head>", og_block + "\n</head>", 1)

    # 5. WebApplication schema: add author/reviewedBy/dateModified
    if is_calc:
        date_mod = CALCS[slug]["dateModified"]

        def patch_webapp(m):
            raw = m.group(1)
            try:
                obj = json.loads(raw)
            except Exception:
                return m.group(0)
            if obj.get("@type") != "WebApplication":
                return m.group(0)
            obj.setdefault("author",       PERSON_REF)
            obj.setdefault("reviewedBy",   PERSON_REF)
            obj.setdefault("dateModified", date_mod)
            return f'<script type="application/ld+json">\n{json.dumps(obj, indent=2, ensure_ascii=False)}\n</script>'

        txt = LDRE.sub(patch_webapp, txt)

    # 6. Article schema: update author to named Person (guides only)
    if is_guide and slug != "guides":
        def patch_article(m):
            raw = m.group(1)
            try:
                obj = json.loads(raw)
            except Exception:
                return m.group(0)
            if obj.get("@type") != "Article":
                return m.group(0)
            obj["author"]              = PERSON_REF
            obj.setdefault("reviewedBy", PERSON_REF)
            return f'<script type="application/ld+json">\n{json.dumps(obj, indent=2, ensure_ascii=False)}\n</script>'

        txt = LDRE.sub(patch_article, txt)

    # 7. BreadcrumbList (idempotent)
    if (is_calc or is_guide) and "BreadcrumbList" not in txt:
        if is_calc:
            bc = breadcrumb_for_calc(slug)
        else:
            title_m = re.search(r"<title>(.*?)</title>", txt)
            title = (title_m.group(1).split("|")[0].strip()
                     if title_m else slug.replace("-", " ").title())
            bc = breadcrumb_for_guide(slug, title)
        txt = txt.replace("</head>", schema_tag(bc) + "\n</head>", 1)

    # 8. WebSite schema on index (idempotent)
    if is_index and "WebSite" not in txt:
        txt = txt.replace("</head>", schema_tag(WEBSITE_SCHEMA) + "\n</head>", 1)

    # 9 & 10. Insert related-calcs + author byline before site-footer (idempotent)
    if "Written and reviewed by" not in txt:
        max_w = "900px" if is_index else ("720px" if is_guide else "820px")

        if is_calc:
            insert = related_calcs_html(slug, max_w) + author_byline_html(max_w)
        else:
            insert = author_byline_html(max_w)

        # Prefer <footer class="site-footer">, else fall back to </body>
        if '<footer class="site-footer">' in txt:
            txt = txt.replace(
                '<footer class="site-footer">',
                insert + '<footer class="site-footer">',
                1,
            )
        else:
            txt = txt.replace("</body>", insert + "</body>", 1)

    if txt != original:
        path.write_text(txt, encoding="utf-8")
        print(f"  [OK] {path.name}")
    else:
        print(f"  [--] {path.name} (unchanged)")


def fix_lang_preconnect(path: Path):
    """Minimal pass for legal/other pages: lang fix + gstatic preconnect."""
    txt = path.read_text(encoding="utf-8")
    original = txt
    txt = re.sub(r'<html\s+lang="en"', '<html lang="en-GB"', txt, count=1)
    if "fonts.gstatic.com" not in txt and "fonts.googleapis.com" in txt:
        txt = txt.replace(
            '<link rel="preconnect" href="https://fonts.googleapis.com" />',
            '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
            1,
        )
    if '"Organization"' not in txt:
        txt = txt.replace("</head>", schema_tag(ORG_SCHEMA) + "\n</head>", 1)
    if txt != original:
        path.write_text(txt, encoding="utf-8")
        print(f"  [OK] {path.name}")
    else:
        print(f"  [--] {path.name} (unchanged)")


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    print("\n=== Calculator pages ===")
    for slug in CALCS:
        p = BASE / f"{slug}.html"
        if p.exists():
            process_file(p, slug, is_calc=True)
        else:
            print(f"  [MISS] {slug}.html")

    print("\n=== Guide pages ===")
    for slug in GUIDES_META:
        p = BASE / f"{slug}.html"
        if p.exists():
            process_file(p, slug, is_guide=True)
        else:
            print(f"  [MISS] {slug}.html")

    print("\n=== Index page ===")
    process_file(BASE / "index.html", "index", is_index=True)

    print("\n=== Legal/other pages (lang + preconnect + org schema) ===")
    for name in ("privacy-policy", "terms", "cookies", "about"):
        p = BASE / f"{name}.html"
        if p.exists():
            fix_lang_preconnect(p)


if __name__ == "__main__":
    main()
