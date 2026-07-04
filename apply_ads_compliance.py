#!/usr/bin/env python3
"""One-time migration: replace the old unconditional AdSense script tag with
the consent-gated CMP + Consent Mode v2 + ad-slot component setup, and insert
ad-slot markup at the correct point in each page.

Safe to re-run: every insertion is guarded so a second run is a no-op.
"""
import os
import re
import glob

BASE = os.path.dirname(os.path.abspath(__file__))

OLD_ADSENSE_RE = re.compile(
    r'[ \t]*<script async src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-3649044515825371"\n'
    r'[ \t]*crossorigin="anonymous"></script>\n'
)

VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'

# Pages with no ad units at all (legal / meta) — still get consent so the CMP
# banner and Consent Mode are consistent site-wide.
LEGAL_PAGES = {
    '404.html', 'about.html', 'privacy-policy.html', 'terms.html', 'cookies.html',
}

# Real calculators with a `#results` panel followed by a `.seo-section` — the
# below-result ad goes immediately before the seo-section.
CATEGORY_A = {
    'break-even-calculator.html', 'budget-planner.html', 'compound-interest-calculator.html',
    'credit-card-payoff-calculator.html', 'currency-converter.html', 'debt-snowball-calculator.html',
    'emergency-fund-calculator.html', 'freelance-rate-calculator.html', 'inflation-calculator.html',
    'investment-return-calculator.html', 'loan-repayment-calculator.html',
    'mortgage-affordability-calculator.html', 'net-worth-calculator.html',
    'pension-contribution-calculator.html', 'rent-vs-buy-calculator.html',
    'salary-to-hourly-calculator.html', 'savings-goal-calculator.html',
    'stamp-duty-calculator.html', 'vat-calculator.html',
}

# Real calculators using `#results-card` with no seo-section — the
# below-result ad goes as the last element inside .container, right before
# the container closes and the calculator's own <script> begins.
CATEGORY_B = {
    'fire-calculator.html', 'isa-vs-pension-calculator.html',
    'salary-sacrifice-calculator.html', 'take-home-pay-calculator.html',
}

# Long-form guide/explainer articles — in-content ad before every 3rd <h2>.
ARTICLE_PAGES = {
    'isa-vs-pension.html', 'stamp-duty-explained.html', 'what-is-fire-movement.html',
    'how-much-can-i-borrow-mortgage.html', 'how-much-tax-will-i-pay.html',
    'guides/how-much-stamp-duty-will-i-pay.html', 'guides/is-salary-sacrifice-worth-it.html',
    'guides/salary-sacrifice-vs-pension-contributions.html',
}

# Navigation hub pages — sidebar + mobile anchor only, no in-page ad units.
HUB_PAGES = {'index.html', 'guides.html'}

AD_ENABLED = CATEGORY_A | CATEGORY_B | ARTICLE_PAGES | HUB_PAGES

BELOW_RESULT_SLOT = (
    '  <div class="ad-slot" data-placement="below-result" '
    'data-ad-format="auto" data-full-width-responsive="true"></div>\n'
)
IN_CONTENT_SLOT = (
    '{indent}<div class="ad-slot" data-placement="in-content" '
    'data-ad-format="auto" data-full-width-responsive="true"></div>\n'
)
FOOTER_SLOTS = (
    '<div class="ad-slot" data-placement="sidebar" data-ad-format="auto"></div>\n'
    '<div class="ad-slot" data-placement="mobile-anchor" data-ad-format="auto">'
    '<button class="ad-anchor-close" aria-label="Close ad" type="button">✕</button></div>\n'
)


def rel(path):
    return os.path.relpath(path, BASE).replace('\\', '/')


def strip_old_adsense(content):
    return OLD_ADSENSE_RE.sub('', content)


def insert_head_assets(content, ad_enabled):
    if 'ads-config.js' in content:
        return content  # already migrated
    if ad_enabled:
        snippet = (
            '  <link rel="stylesheet" href="/ads.css" />\n'
            '  <script src="/ads-config.js"></script>\n'
            '  <script src="/consent.js"></script>\n'
            '  <script src="/ads.js"></script>\n'
        )
    else:
        snippet = (
            '  <script src="/ads-config.js"></script>\n'
            '  <script src="/consent.js"></script>\n'
        )
    return content.replace(VIEWPORT_TAG + '\n', VIEWPORT_TAG + '\n' + snippet, 1)


def insert_footer_manage_link(content):
    pattern = re.compile(r'(<a href="/cookies">[^<]*</a>\n)(\s*)(</nav>)')
    if 'data-consent-manage' in content:
        return content
    def _sub(m):
        return m.group(1) + m.group(2) + '<a href="#" data-consent-manage="1">Manage Cookies</a>\n' + m.group(2) + m.group(3)
    return pattern.sub(_sub, content, count=1)


def insert_body_slots(content):
    if 'data-placement="sidebar"' in content:
        return content
    return re.sub(r'\n</body>', '\n' + FOOTER_SLOTS + '</body>', content, count=1)


def insert_below_result_a(content):
    if 'data-placement="below-result"' in content:
        return content
    marker = '<div class="seo-section">'
    idx = content.find(marker)
    if idx == -1:
        return content
    return content[:idx] + BELOW_RESULT_SLOT + '\n' + content[idx:]


def insert_below_result_b(content):
    if 'data-placement="below-result"' in content:
        return content
    return re.sub(
        r'\n</div>\n\n<script>',
        '\n' + BELOW_RESULT_SLOT + '</div>\n\n<script>',
        content, count=1,
    )


def insert_in_content(content):
    if 'data-placement="in-content"' in content:
        return content
    lines = content.split('\n')
    out = []
    h2_count = 0
    for line in lines:
        m = re.match(r'^(\s*)<h2>', line)
        if m:
            h2_count += 1
            if h2_count > 2 and (h2_count - 2) % 3 == 1:
                out.append(IN_CONTENT_SLOT.format(indent=m.group(1)).rstrip('\n'))
        out.append(line)
    return '\n'.join(out)


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    name = rel(path)
    ad_enabled = name in AD_ENABLED

    content = strip_old_adsense(original)
    content = insert_head_assets(content, ad_enabled)
    content = insert_footer_manage_link(content)

    if ad_enabled:
        content = insert_body_slots(content)
        if name in CATEGORY_A:
            content = insert_below_result_a(content)
        elif name in CATEGORY_B:
            content = insert_below_result_b(content)
        elif name in ARTICLE_PAGES:
            content = insert_in_content(content)
        # HUB_PAGES: sidebar + anchor only, already added above

    if content != original:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    return False


def main():
    html_files = sorted(glob.glob(os.path.join(BASE, '*.html')) + glob.glob(os.path.join(BASE, 'guides', '*.html')))
    changed = []
    unknown = []
    for path in html_files:
        name = rel(path)
        if name not in LEGAL_PAGES and name not in AD_ENABLED:
            unknown.append(name)
        if process(path):
            changed.append(name)

    print(f'Updated {len(changed)} files:')
    for f in changed:
        print(f'  + {f}')
    if unknown:
        print(f'\nWARNING: {len(unknown)} files not classified (no consent/ads assets added):')
        for f in unknown:
            print(f'  ! {f}')


if __name__ == '__main__':
    main()
