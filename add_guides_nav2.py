import os, re

BASE = r"C:\finance-calculators\calculators-updated"

GUIDES_LINK = '<a href="/guides" class="site-nav-guides">Guides</a>'

def has_guides_link(content):
    return 'href="/guides"' in content or "href='/guides'" in content

def add_guides_to_site_nav(content, filepath):
    if has_guides_link(content):
        print(f"  [skip] already has /guides: {os.path.basename(filepath)}")
        return content
    pattern = r'(<a[^>]+class="site-nav-logo"[^>]*>.*?</a>)'
    replacement = r'\1\n  ' + GUIDES_LINK
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content == content:
        print(f"  [warn] logo not found: {os.path.basename(filepath)}")
    else:
        print(f"  [ok] added guides link: {os.path.basename(filepath)}")
    return new_content

remaining = [
    "loan-repayment-calculator.html",
    "salary-to-hourly-calculator.html",
    "credit-card-payoff-calculator.html",
    "break-even-calculator.html",
    "inflation-calculator.html",
    "investment-return-calculator.html",
    "currency-converter.html",
    "debt-snowball-calculator.html",
    "vat-calculator.html",
]

for fname in remaining:
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"  [missing] {fname}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = add_guides_to_site_nav(content, fpath)
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Done.")
