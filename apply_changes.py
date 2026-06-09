"""
Bulk-applies to every existing HTML page:
  1. Favicon link
  2. Canonical URL
  3. Open Graph + Twitter card meta tags
  4. Footer CSS + HTML
  5. Cookie consent banner
  6. WebApplication JSON-LD schema (calculator pages only)
  7. Updates existing <title> to include brand suffix if missing
"""
import re, os

BASE_URL = "https://calculators.finance"

# ---------------------------------------------------------------------------
# Per-page metadata
# ---------------------------------------------------------------------------
PAGES = {
    "index.html": {
        "slug": "",
        "title": "UK Finance Calculators — Free Tools for Every Money Decision | Calculators.Finance",
        "desc": "23 free UK finance calculators. Tax, mortgages, savings, investments, debt, pensions, FIRE, ISA vs pension, salary sacrifice and more. Instant results, no signup.",
        "calculator": False,
        "app_name": None,
    },
    "take-home-pay-calculator.html": {
        "slug": "take-home-pay-calculator",
        "title": "Take-Home Pay Calculator UK 2025/26 | Calculators.Finance",
        "desc": "Calculate your exact UK take-home pay after income tax, National Insurance, pension, student loan and salary sacrifice. Scottish rates, all NI letters. 2025/26 HMRC rates.",
        "calculator": True,
        "app_name": "UK Take-Home Pay Calculator",
    },
    "stamp-duty-calculator.html": {
        "slug": "stamp-duty-calculator",
        "title": "Stamp Duty Calculator UK 2025 — SDLT, LBTT & LTT | Calculators.Finance",
        "desc": "Calculate stamp duty land tax (SDLT) for England, LBTT for Scotland and LTT for Wales. Covers first-time buyers, additional properties and 2025 thresholds.",
        "calculator": True,
        "app_name": "UK Stamp Duty Calculator",
    },
    "mortgage-affordability-calculator.html": {
        "slug": "mortgage-affordability-calculator",
        "title": "Mortgage Affordability Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate how much you can borrow for a UK mortgage. Enter income, deposit and outgoings to see maximum borrowing, monthly repayments and affordability ratios instantly.",
        "calculator": True,
        "app_name": "UK Mortgage Affordability Calculator",
    },
    "salary-sacrifice-calculator.html": {
        "slug": "salary-sacrifice-calculator",
        "title": "Salary Sacrifice Calculator UK 2025/26 | Calculators.Finance",
        "desc": "Calculate the true net cost of UK salary sacrifice for pension, cycle to work, EV lease and childcare. See exact income tax and NI savings. 2025/26 HMRC rates.",
        "calculator": True,
        "app_name": "UK Salary Sacrifice Calculator",
    },
    "pension-contribution-calculator.html": {
        "slug": "pension-contribution-calculator",
        "title": "Pension Contribution Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate how much to contribute to your UK pension. See projected pension pot, employer contributions, tax relief and estimated retirement income. 2025/26 rates.",
        "calculator": True,
        "app_name": "UK Pension Contribution Calculator",
    },
    "isa-vs-pension-calculator.html": {
        "slug": "isa-vs-pension-calculator",
        "title": "ISA vs Pension Calculator UK 2025/26 | Calculators.Finance",
        "desc": "Compare ISA vs pension for UK investors. Side-by-side analysis showing which gives more retirement income based on your current and future tax rates. 2025/26.",
        "calculator": True,
        "app_name": "UK ISA vs Pension Calculator",
    },
    "rent-vs-buy-calculator.html": {
        "slug": "rent-vs-buy-calculator",
        "title": "Rent vs Buy Calculator UK 2025 | Calculators.Finance",
        "desc": "Is it cheaper to rent or buy a home in the UK? Compare the true 5, 10 and 20-year cost including all fees, maintenance, stamp duty and equity growth.",
        "calculator": True,
        "app_name": "UK Rent vs Buy Calculator",
    },
    "freelance-rate-calculator.html": {
        "slug": "freelance-rate-calculator",
        "title": "Freelance Rate Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate your minimum UK freelance day rate and hourly rate. Factor in taxes, holidays, sick days, expenses and profit margin to find a rate that works.",
        "calculator": True,
        "app_name": "UK Freelance Rate Calculator",
    },
    "salary-to-hourly-calculator.html": {
        "slug": "salary-to-hourly-calculator",
        "title": "Salary to Hourly Rate Calculator UK 2025 | Calculators.Finance",
        "desc": "Convert any UK annual salary to an hourly rate. Enter your salary and working hours to see your exact hourly, daily, weekly and monthly pay breakdown instantly.",
        "calculator": True,
        "app_name": "UK Salary to Hourly Calculator",
    },
    "loan-repayment-calculator.html": {
        "slug": "loan-repayment-calculator",
        "title": "Loan Repayment Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate monthly loan repayments for any UK loan. Enter amount, interest rate and term to see your exact monthly payment, total interest and amortisation schedule.",
        "calculator": True,
        "app_name": "UK Loan Repayment Calculator",
    },
    "savings-goal-calculator.html": {
        "slug": "savings-goal-calculator",
        "title": "Savings Goal Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate how long to reach your UK savings goal. Enter your target, monthly savings and interest rate to get your exact timeline and required monthly contribution.",
        "calculator": True,
        "app_name": "UK Savings Goal Calculator",
    },
    "credit-card-payoff-calculator.html": {
        "slug": "credit-card-payoff-calculator",
        "title": "Credit Card Payoff Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate how long to pay off your UK credit card debt. Enter balance, interest rate and monthly payment to see your payoff date and total interest paid.",
        "calculator": True,
        "app_name": "UK Credit Card Payoff Calculator",
    },
    "compound-interest-calculator.html": {
        "slug": "compound-interest-calculator",
        "title": "Compound Interest Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate compound interest on UK savings or investments. See exactly how your money grows over time with different rates, contribution amounts and compounding periods.",
        "calculator": True,
        "app_name": "UK Compound Interest Calculator",
    },
    "emergency-fund-calculator.html": {
        "slug": "emergency-fund-calculator",
        "title": "Emergency Fund Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate how much you need in your UK emergency fund. Enter monthly expenses to see recommended 3, 6 and 12-month safety net targets and a savings plan.",
        "calculator": True,
        "app_name": "UK Emergency Fund Calculator",
    },
    "fire-calculator.html": {
        "slug": "fire-calculator",
        "title": "FIRE Calculator UK 2025 — Financial Independence, Retire Early | Calculators.Finance",
        "desc": "Calculate your UK FIRE number, years to financial independence, Coast FIRE and Lean FIRE targets. Real vs nominal projections with inflation adjustment.",
        "calculator": True,
        "app_name": "UK FIRE Calculator",
    },
    "net-worth-calculator.html": {
        "slug": "net-worth-calculator",
        "title": "Net Worth Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate your UK net worth instantly. Add assets and liabilities — property, savings, investments, pensions, loans — to see your true financial position.",
        "calculator": True,
        "app_name": "UK Net Worth Calculator",
    },
    "budget-planner.html": {
        "slug": "budget-planner",
        "title": "Monthly Budget Planner UK 2025 | Calculators.Finance",
        "desc": "Plan your monthly UK budget with our free budget planner. Enter income and expenses to see exactly where your money goes and how much you have left to save.",
        "calculator": True,
        "app_name": "UK Monthly Budget Planner",
    },
    "inflation-calculator.html": {
        "slug": "inflation-calculator",
        "title": "Inflation Calculator UK 2025 — What Is £X Worth Today? | Calculators.Finance",
        "desc": "Calculate the real value of money adjusted for UK inflation (CPI/RPI). See what any amount from any year is worth in today's money using official ONS data.",
        "calculator": True,
        "app_name": "UK Inflation Calculator",
    },
    "investment-return-calculator.html": {
        "slug": "investment-return-calculator",
        "title": "Investment Return Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate the return on any UK investment. Enter initial amount, contributions, rate of return and time period to see investment growth, real returns and CAGR.",
        "calculator": True,
        "app_name": "UK Investment Return Calculator",
    },
    "break-even-calculator.html": {
        "slug": "break-even-calculator",
        "title": "Break-Even Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate your business break-even point instantly. Enter fixed costs, variable costs and selling price to see exactly how many units you need to sell to break even.",
        "calculator": True,
        "app_name": "UK Break-Even Calculator",
    },
    "debt-snowball-calculator.html": {
        "slug": "debt-snowball-calculator",
        "title": "Debt Snowball Calculator UK 2025 | Calculators.Finance",
        "desc": "Calculate your debt snowball payoff plan. Enter all your debts to see the exact payoff order, total interest saved vs minimum payments and your debt-free date.",
        "calculator": True,
        "app_name": "UK Debt Snowball Calculator",
    },
    "currency-converter.html": {
        "slug": "currency-converter",
        "title": "Currency Converter — GBP to USD, EUR, JPY & More | Calculators.Finance",
        "desc": "Convert GBP to USD, EUR, JPY and 30+ currencies. Live exchange rates updated daily with historical context and multi-currency comparison built in.",
        "calculator": True,
        "app_name": "Currency Converter",
    },
    "vat-calculator.html": {
        "slug": "vat-calculator",
        "title": "VAT Calculator UK 2025 — Add or Remove VAT Instantly | Calculators.Finance",
        "desc": "Add or remove UK VAT from any price instantly. Calculate 20%, 5% and 0% VAT rates, see the net and gross breakdown and work out your quarterly VAT return.",
        "calculator": True,
        "app_name": "UK VAT Calculator",
    },
}

# ---------------------------------------------------------------------------
# Reusable HTML snippets
# ---------------------------------------------------------------------------
FOOTER_CSS = """
  <style>
    .site-footer {
      background: #fff; border-top: 1px solid #e2e8f0;
      padding: 24px 32px; margin-top: 40px;
      font-family: 'Inter', sans-serif; font-size: 12px; color: #64748b;
    }
    .site-footer-inner {
      max-width: 900px; margin: 0 auto;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 12px;
    }
    .site-footer-links { display: flex; gap: 20px; flex-wrap: wrap; }
    .site-footer-links a { color: #64748b; text-decoration: none; transition: color 0.15s; }
    .site-footer-links a:hover { color: #2563eb; }
    @media (max-width: 520px) {
      .site-footer { padding: 20px 16px; }
      .site-footer-inner { flex-direction: column; align-items: flex-start; gap: 8px; }
    }
  </style>
</head>"""

FOOTER_HTML = """
<footer class="site-footer">
  <div class="site-footer-inner">
    <span>© 2025 Calculators.Finance — For informational purposes only. Not financial advice.</span>
    <nav class="site-footer-links">
      <a href="/about">About</a>
      <a href="/privacy-policy">Privacy Policy</a>
      <a href="/terms">Terms of Use</a>
      <a href="/cookies">Cookie Policy</a>
    </nav>
  </div>
</footer>

<div id="cookie-banner" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #e2e8f0;padding:14px 24px;z-index:9999;font-family:'Inter',sans-serif;font-size:13px;color:#475569;box-shadow:0 -2px 12px rgba(0,0,0,0.06);">
  <div style="max-width:900px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
    <span>We use cookies for analytics and advertising. See our <a href="/cookies" style="color:#2563eb;text-decoration:none;">Cookie Policy</a>.</span>
    <div style="display:flex;gap:8px;flex-shrink:0;">
      <button onclick="acceptCookies()" style="background:#2563eb;color:#fff;border:none;border-radius:6px;padding:8px 18px;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;cursor:pointer;">Accept</button>
      <button onclick="declineCookies()" style="background:transparent;color:#64748b;border:1px solid #e2e8f0;border-radius:6px;padding:8px 18px;font-family:'Inter',sans-serif;font-size:13px;cursor:pointer;">Decline</button>
    </div>
  </div>
</div>
<script>
  (function(){
    if(!localStorage.getItem('cookie_consent')){
      document.getElementById('cookie-banner').style.display='block';
    }
  })();
  function acceptCookies(){
    localStorage.setItem('cookie_consent','accepted');
    document.getElementById('cookie-banner').style.display='none';
  }
  function declineCookies(){
    localStorage.setItem('cookie_consent','declined');
    document.getElementById('cookie-banner').style.display='none';
  }
</script>
</body>"""


def web_app_schema(meta):
    url = BASE_URL + ("/" + meta["slug"] if meta["slug"] else "/")
    return f"""
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "{meta['app_name']}",
    "url": "{url}",
    "applicationCategory": "FinanceApplication",
    "operatingSystem": "Any",
    "browserRequirements": "Requires JavaScript",
    "offers": {{
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "GBP"
    }},
    "description": "{meta['desc']}"
  }}
  </script>
</head>"""


def og_tags(meta):
    url = BASE_URL + ("/" + meta["slug"] if meta["slug"] else "/")
    return f"""  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="canonical" href="{url}" />
  <meta property="og:title" content="{meta['title']}" />
  <meta property="og:description" content="{meta['desc']}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Calculators.Finance" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{meta['title']}" />
  <meta name="twitter:description" content="{meta['desc']}" />"""


def process_file(filepath, meta):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1. Update <title>
    new_title = f"  <title>{meta['title']}</title>"
    html, n = re.subn(r'[ \t]*<title>.*?</title>', new_title, html, count=1, flags=re.DOTALL)
    if n:
        changed = True

    # 2. Update <meta name="description">
    new_desc = f'  <meta name="description" content="{meta["desc"]}" />'
    html, n = re.subn(r'[ \t]*<meta name="description"[^>]*/>', new_desc, html, count=1)
    if n:
        changed = True

    # 3. Remove any existing canonical / og: / twitter: / favicon tags to avoid duplicates
    html = re.sub(r'[ \t]*<link rel="canonical"[^>]*/>\n?', '', html)
    html = re.sub(r'[ \t]*<link rel="icon"[^>]*/>\n?', '', html)
    html = re.sub(r'[ \t]*<meta property="og:[^>]*/>\n?', '', html)
    html = re.sub(r'[ \t]*<meta name="twitter:[^>]*/>\n?', '', html)

    # 4. Insert og+canonical block just before </head>
    og_block = og_tags(meta) + "\n"
    html = re.sub(r'([ \t]*</head>)', og_block + r'\1', html, count=1)
    changed = True

    # 5. Add footer CSS before </head>  (replace </head> with style block + </head>)
    if 'class="site-footer"' not in html:
        html = html.replace('</head>', FOOTER_CSS, 1)
        changed = True

    # 6. Add WebApplication schema before </head> (calculator pages only)
    if meta["calculator"] and meta["app_name"]:
        if '"@type": "WebApplication"' not in html:
            html = html.replace('</head>', web_app_schema(meta), 1)
            changed = True

    # 7. Add footer + cookie banner before </body>
    if 'class="site-footer"' not in html:
        html = html.replace('</body>', FOOTER_HTML, 1)
        changed = True
    elif '</footer>' in html and 'cookie-banner' not in html:
        # footer present but no cookie banner yet — insert banner before </body>
        cookie_banner_only = FOOTER_HTML.split('<footer')[1]  # everything from footer open tag
        html = html.replace('</body>', '<footer' + cookie_banner_only, 1)
        changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Updated: {os.path.basename(filepath)}")
    else:
        print(f"  Skipped (no changes): {os.path.basename(filepath)}")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

print("Applying changes to all pages...")
for filename, meta in PAGES.items():
    filepath = os.path.join(script_dir, filename)
    if os.path.exists(filepath):
        process_file(filepath, meta)
    else:
        print(f"  MISSING: {filename}")

print("\nDone.")
