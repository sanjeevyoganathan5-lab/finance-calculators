import os, re

BASE = r"C:\finance-calculators\calculators-updated"

# Pages that use .site-nav pattern (calculators + legal pages)
# Add Guides link between logo and spacer
SITE_NAV_FILES = [
    "take-home-pay-calculator.html",
    "stamp-duty-calculator.html",
    "mortgage-affordability-calculator.html",
    "isa-vs-pension-calculator.html",
    "fire-calculator.html",
    "salary-sacrifice-calculator.html",
    "pension-contribution-calculator.html",
    "rent-vs-buy-calculator.html",
    "compound-interest-calculator.html",
    "savings-goal-calculator.html",
    "budget-planner.html",
    "debt-payoff-calculator.html",
    "emergency-fund-calculator.html",
    "net-worth-calculator.html",
    "investment-returns-calculator.html",
    "dividend-yield-calculator.html",
    "freelance-rate-calculator.html",
    "vehicle-cost-calculator.html",
    "cost-of-living-calculator.html",
    "student-loan-repayment-calculator.html",
    "inheritance-tax-calculator.html",
    "capital-gains-tax-calculator.html",
    "child-benefit-calculator.html",
    "about.html",
    "privacy-policy.html",
    "terms.html",
    "cookies.html",
]

# index.html uses a different nav pattern — nav-right based
INDEX_FILE = "index.html"

# The guides link HTML to insert for site-nav pages
GUIDES_LINK = '<a href="/guides" class="site-nav-guides">Guides</a>'

# Detect if guides link already present in file
def has_guides_link(content):
    return 'href="/guides"' in content or "href='/guides'" in content

def add_guides_to_site_nav(content, filepath):
    """Insert Guides link after the logo link in .site-nav"""
    if has_guides_link(content):
        print(f"  [skip] already has /guides: {os.path.basename(filepath)}")
        return content

    # Match the logo anchor inside site-nav and insert guides link after it
    pattern = r'(<a[^>]+class="site-nav-logo"[^>]*>.*?</a>)'
    replacement = r'\1\n  ' + GUIDES_LINK
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content == content:
        print(f"  [warn] logo not found in site-nav: {os.path.basename(filepath)}")
    else:
        print(f"  [ok] added guides link: {os.path.basename(filepath)}")
    return new_content

def add_guides_to_index_nav(content, filepath):
    """Insert Guides link inside nav-right div in index.html"""
    if has_guides_link(content):
        print(f"  [skip] already has /guides: {os.path.basename(filepath)}")
        return content

    pattern = r'(<div[^>]+class="nav-right"[^>]*>)'
    replacement = r'\1\n      <a href="/guides" style="font-size:13px;font-weight:500;color:#64748b;text-decoration:none;" onmouseover="this.style.color=\'#2563eb\'" onmouseout="this.style.color=\'#64748b\'">Guides</a>'
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content == content:
        # Fallback: try inserting before </nav>
        pattern2 = r'(</nav>)'
        replacement2 = '      <a href="/guides" style="font-size:13px;font-weight:500;color:#64748b;text-decoration:none;">Guides</a>\n    ' + r'\1'
        new_content = re.sub(pattern2, replacement2, content, count=1)
        if new_content == content:
            print(f"  [warn] nav-right not found: {os.path.basename(filepath)}")
        else:
            print(f"  [ok] added guides link (fallback): {os.path.basename(filepath)}")
    else:
        print(f"  [ok] added guides link: {os.path.basename(filepath)}")
    return new_content

# Related guide links for 5 calculator pages
RELATED_GUIDES = {
    "take-home-pay-calculator.html": {
        "guide_url": "/how-much-tax-will-i-pay",
        "guide_title": "How Much Tax Will I Pay on My Salary?",
    },
    "stamp-duty-calculator.html": {
        "guide_url": "/stamp-duty-explained",
        "guide_title": "How Much Stamp Duty Will I Pay?",
    },
    "mortgage-affordability-calculator.html": {
        "guide_url": "/how-much-can-i-borrow-mortgage",
        "guide_title": "How Much Can I Borrow for a Mortgage?",
    },
    "isa-vs-pension-calculator.html": {
        "guide_url": "/isa-vs-pension",
        "guide_title": "ISA vs Pension: Which Is Better?",
    },
    "fire-calculator.html": {
        "guide_url": "/what-is-fire-movement",
        "guide_title": "What Is the FIRE Movement?",
    },
}

RELATED_GUIDE_HTML = """
  <div style="margin:0 auto 24px;max-width:760px;padding:0 16px;">
    <a href="{url}" style="display:inline-flex;align-items:center;gap:8px;background:rgba(37,99,235,.06);border:1px solid rgba(37,99,235,.18);border-radius:6px;padding:10px 16px;font-family:'Inter',sans-serif;font-size:13px;font-weight:500;color:#2563eb;text-decoration:none;transition:all .15s;" onmouseover="this.style.background='rgba(37,99,235,.12)'" onmouseout="this.style.background='rgba(37,99,235,.06)'">
      <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      Related guide: {title} →
    </a>
  </div>"""

def add_related_guide(content, filepath):
    fname = os.path.basename(filepath)
    if fname not in RELATED_GUIDES:
        return content
    info = RELATED_GUIDES[fname]
    if info["guide_url"] in content:
        print(f"  [skip] related guide already present: {fname}")
        return content
    guide_html = RELATED_GUIDE_HTML.format(url=info["guide_url"], title=info["guide_title"])
    # Insert after opening <main> or <div class="calculator-container"> or before first <h1 — try several anchors
    inserted = False
    for pattern in [
        r'(<main[^>]*>)',
        r'(<div[^>]+class="[^"]*calculator-wrapper[^"]*"[^>]*>)',
        r'(<div[^>]+class="[^"]*hero[^"]*"[^>]*>)',
        r'(<div[^>]+id="calculator"[^>]*>)',
    ]:
        m = re.search(pattern, content)
        if m:
            insert_pos = m.end()
            new_content = content[:insert_pos] + guide_html + content[insert_pos:]
            print(f"  [ok] added related guide link: {fname}")
            return new_content
    # Last resort: insert before closing </body>
    new_content = content.replace("</body>", guide_html + "\n</body>", 1)
    if new_content != content:
        print(f"  [ok] added related guide link (body fallback): {fname}")
        return new_content
    print(f"  [warn] could not find insertion point for related guide: {fname}")
    return content

# Process site-nav files
print("=== Adding Guides nav link to site-nav pages ===")
for fname in SITE_NAV_FILES:
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"  [missing] {fname}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = add_guides_to_site_nav(content, fpath)
    new_content = add_related_guide(new_content, fpath)
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)

# Process index.html
print("\n=== Adding Guides nav link to index.html ===")
index_path = os.path.join(BASE, INDEX_FILE)
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = add_guides_to_index_nav(content, index_path)
    if new_content != content:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
else:
    print(f"  [missing] {INDEX_FILE}")

print("\nDone.")
