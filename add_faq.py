"""
Injects FAQ sections (visible HTML + FAQPage JSON-LD) into the 3 top calculators.
Run from inside calculators-updated/.
"""
import re, os, json

BASE_URL = "https://calculators.finance"

# ---------------------------------------------------------------------------
# FAQ data for each page
# ---------------------------------------------------------------------------

THP_FAQS = [
    {
        "q": "How much tax do I pay on a £30,000 salary in 2025/26?",
        "a": "On a £30,000 salary in 2025/26 (England, no pension, no student loan), you pay £3,486 in income tax and £1,394.40 in National Insurance, leaving a take-home pay of £25,119.60 per year (£2,093.30/month). Income tax is calculated on the £17,430 above the £12,570 personal allowance at 20%."
    },
    {
        "q": "What is the personal allowance for 2025/26?",
        "a": "The personal allowance for 2025/26 is £12,570. This is the amount you can earn before paying any income tax. It has been frozen at this level since 2021/22. If your income exceeds £100,000, your personal allowance is reduced by £1 for every £2 earned above that threshold, reaching £0 at £125,140."
    },
    {
        "q": "What are the National Insurance rates for employees in 2025/26?",
        "a": "For 2025/26, employees pay NI at 8% on earnings between £12,570 and £50,270, and 2% on earnings above £50,270. The Primary Threshold (PT) of £12,570 and Upper Earnings Limit (UEL) of £50,270 are both frozen for 2025/26. There is no NI on earnings below £12,570."
    },
    {
        "q": "How does salary sacrifice reduce my tax and NI?",
        "a": "Salary sacrifice reduces your gross pay before income tax and National Insurance are calculated. For example, a £200/month pension sacrifice costs a basic-rate taxpayer only £144/month net (saving 20% income tax + 8% NI = 28%). For higher-rate taxpayers the saving is greater: 40% tax + 2% NI = 42% saving, making a £200 sacrifice cost only £116/month net."
    },
    {
        "q": "What is the 60% tax trap and who does it affect?",
        "a": "The 60% effective marginal tax rate affects people earning between £100,000 and £125,140. In this range, every extra £2 earned causes a £1 reduction in the personal allowance. The result is that each additional £1 of income is taxed at 40% directly, plus you lose 50p of allowance which is also taxed at 40% — effectively a 60% rate. Salary sacrifice into a pension is the most effective way to reduce income below £100,000 and escape this trap."
    },
    {
        "q": "Does a student loan affect my take-home pay?",
        "a": "Yes. Student loan repayments are deducted from pay above the relevant threshold. For Plan 2 loans (most graduates from 2012 onwards), repayments are 9% on earnings above £27,295 in 2025/26. On a £35,000 salary, that is 9% × (£35,000 − £27,295) = £693.45/year. Repayments show on your payslip alongside tax and NI and reduce your net pay accordingly."
    },
]

SDLT_FAQS = [
    {
        "q": "What are the stamp duty rates in England in 2025/26?",
        "a": "In England and Northern Ireland for 2025/26, stamp duty (SDLT) is charged at 0% on the first £250,000; 5% on £250,001–£925,000; 10% on £925,001–£1,500,000; and 12% above £1,500,000. These are marginal rates — you only pay each rate on the portion within that band, not the whole purchase price."
    },
    {
        "q": "How much stamp duty does a first-time buyer pay?",
        "a": "First-time buyers in England and Northern Ireland pay no stamp duty on properties up to £425,000, and 5% on the portion between £425,001 and £625,000. For properties above £625,000, first-time buyer relief does not apply and the standard rates kick in. In Scotland (LBTT) and Wales (LTT), first-time buyer thresholds differ — use this calculator to see the exact figures for each country."
    },
    {
        "q": "How much stamp duty on a £400,000 property in 2025?",
        "a": "For a home mover (not first-time buyer) buying at £400,000 in England: 0% on the first £250,000 = £0; 5% on £150,000 (£250,001–£400,000) = £7,500. Total SDLT = £7,500. A first-time buyer at the same price pays £0 (the full price is below the £425,000 first-time buyer threshold). An additional property buyer pays an extra 5% surcharge on every band: total £27,500."
    },
    {
        "q": "What is the additional property stamp duty surcharge in 2025?",
        "a": "Buyers purchasing an additional residential property (buy-to-let, second home, holiday home) in England and Northern Ireland pay a 5% surcharge on top of standard rates on every band from April 2025. On a £300,000 additional property, the surcharge alone adds £15,000 to the SDLT bill. The higher rates apply from the day of completion."
    },
    {
        "q": "Do you pay stamp duty in Scotland?",
        "a": "Scotland does not use Stamp Duty Land Tax. Instead, buyers pay Land and Buildings Transaction Tax (LBTT), which has different rates and thresholds. For 2025/26, LBTT rates are: 0% up to £145,000; 2% on £145,001–£250,000; 5% on £250,001–£325,000; 10% on £325,001–£750,000; 12% above £750,000. First-time buyers get a relief raising the 0% threshold to £175,000."
    },
    {
        "q": "What counts as a first-time buyer for stamp duty purposes?",
        "a": "A first-time buyer is someone who has never previously owned a residential property anywhere in the world — including properties inherited, received as a gift, or owned abroad. For joint purchases, all buyers must be first-time buyers to qualify for the relief. You cannot claim the relief if you have ever been named on a property title deeds, even if the property was later sold."
    },
]

MORTGAGE_FAQS = [
    {
        "q": "How much can I borrow for a mortgage in the UK in 2025?",
        "a": "Most UK lenders will lend 4 to 4.5 times your annual gross income. For a single applicant earning £50,000, that is typically £200,000–£225,000. For joint buyers, lenders use a combined income. Some lenders — particularly for professionals or high earners — offer up to 5 or 5.5 times income, but these products usually require a larger deposit and a good credit history."
    },
    {
        "q": "What deposit do I need to buy a house in 2025?",
        "a": "The minimum deposit for most UK mortgages is 5% of the purchase price. However, a 10% deposit typically unlocks significantly better interest rates, and 20%+ gives access to the best rates available. With a 5% deposit (95% LTV), you will generally face higher monthly payments due to both the larger loan and a higher interest rate. Government schemes like the Mortgage Guarantee Scheme may help buyers with smaller deposits."
    },
    {
        "q": "How do lenders calculate mortgage affordability?",
        "a": "Lenders assess affordability in two ways: the income multiple (typically 4–4.5x gross income) and a detailed expenditure check. They review bank statements, credit commitments (loans, car finance, credit card minimums), household bills, and childcare costs. They then stress-test the monthly payment at a higher interest rate (typically 3% above the current rate) to ensure you could still afford it if rates rose."
    },
    {
        "q": "Do existing debts affect how much mortgage I can borrow?",
        "a": "Yes, significantly. Existing monthly debt commitments — car finance, personal loans, credit card minimums, student loan repayments — directly reduce your disposable income and therefore your maximum borrowing. A lender will subtract all monthly commitments from your net income before calculating affordability. Clearing or reducing debts before applying can meaningfully increase what you are offered."
    },
    {
        "q": "What is the difference between the mortgage term and the loan term?",
        "a": "These are usually the same: the term is the number of years over which the loan is repaid. Most UK residential mortgages are on a 25-year term, though 30 and 35-year terms are increasingly common as house prices have risen. A longer term reduces monthly payments but significantly increases total interest paid. This calculator shows both monthly payments and total interest so you can compare terms directly."
    },
    {
        "q": "How does the interest rate affect my monthly mortgage payment?",
        "a": "The interest rate has a substantial effect on monthly payments. On a £250,000 repayment mortgage over 25 years: at 4% the monthly payment is around £1,319; at 5% it is approximately £1,461; at 6% around £1,610. A 1 percentage point rise costs roughly £140/month on a £250,000 mortgage. This is why affordability stress-testing at higher rates is part of the lending assessment."
    },
]

# ---------------------------------------------------------------------------
# FAQ HTML builder (matches seo-card style for THP, seo-section for others)
# ---------------------------------------------------------------------------

def build_faq_html_seocard(faqs):
    items = ""
    for i, faq in enumerate(faqs):
        items += f"""  <details class="faq-item" {'open' if i == 0 else ''}>
    <summary class="faq-q">{faq['q']}</summary>
    <p class="faq-a">{faq['a']}</p>
  </details>
"""
    return f"""
  <div class="seo-card" style="margin-top:16px;">
    <h2>Frequently Asked Questions</h2>
{items}  </div>
"""

def build_faq_html_seosection(faqs, extra_style=""):
    items = ""
    for i, faq in enumerate(faqs):
        items += f"""  <details class="faq-item" {'open' if i == 0 else ''}>
    <summary class="faq-q">{faq['q']}</summary>
    <p class="faq-a">{faq['a']}</p>
  </details>
"""
    return f"""
  <div class="seo-section"{extra_style}>
    <h2>Frequently Asked Questions</h2>
{items}  </div>
"""

FAQ_STYLE = """
  <style>
    .faq-item { border-bottom: 1px solid var(--border); padding: 12px 0; }
    .faq-item:last-child { border-bottom: none; }
    .faq-item summary { list-style: none; cursor: pointer; font-size: 14px; font-weight: 600; color: var(--text); display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .faq-item summary::-webkit-details-marker { display: none; }
    .faq-item summary::after { content: '+'; font-size: 18px; font-weight: 400; color: var(--accent); flex-shrink: 0; }
    .faq-item[open] summary::after { content: '−'; }
    .faq-a { font-family: 'DM Mono', monospace; font-size: 12px; color: var(--muted); line-height: 1.8; font-weight: 300; margin-top: 10px; }
  </style>
"""

FAQ_STYLE_SANS_DM = """
  <style>
    .faq-item { border-bottom: 1px solid var(--border); padding: 12px 0; }
    .faq-item:last-child { border-bottom: none; }
    .faq-item summary { list-style: none; cursor: pointer; font-size: 14px; font-weight: 600; color: var(--text); display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .faq-item summary::-webkit-details-marker { display: none; }
    .faq-item summary::after { content: '+'; font-size: 18px; font-weight: 400; color: var(--accent); flex-shrink: 0; }
    .faq-item[open] summary::after { content: '−'; }
    .faq-a { font-size: 13px; color: var(--muted); line-height: 1.8; margin-top: 10px; }
  </style>
"""

def build_faq_schema(faqs, url):
    items = []
    for faq in faqs:
        items.append({
            "@type": "Question",
            "name": faq["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["a"]
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }
    return f'  <script type="application/ld+json">\n  {json.dumps(schema, indent=2, ensure_ascii=False)}\n  </script>\n'


# ---------------------------------------------------------------------------
# Per-file patch
# ---------------------------------------------------------------------------

def patch_thp(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'Frequently Asked Questions' in html:
        print("  take-home-pay: FAQ already present, skipping.")
        return

    # Insert FAQ style before </head>
    html = html.replace('</head>', FAQ_STYLE + '</head>', 1)

    # Insert FAQPage schema before </head>
    schema = build_faq_schema(THP_FAQS, BASE_URL + "/take-home-pay-calculator")
    html = html.replace('</head>', schema + '</head>', 1)

    # Insert FAQ HTML after the closing </div> of the seo-card
    faq_html = build_faq_html_seocard(THP_FAQS)
    html = html.replace('  </div>\n\n</div>\n\n<script>', faq_html + '</div>\n\n<script>', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  take-home-pay: FAQ injected.")


def patch_sdlt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'Frequently Asked Questions' in html:
        print("  stamp-duty: FAQ already present, skipping.")
        return

    html = html.replace('</head>', FAQ_STYLE_SANS_DM + '</head>', 1)
    schema = build_faq_schema(SDLT_FAQS, BASE_URL + "/stamp-duty-calculator")
    html = html.replace('</head>', schema + '</head>', 1)

    faq_html = build_faq_html_seosection(SDLT_FAQS)
    # Insert after the closing </div> of seo-section, before outer </div>
    html = html.replace('  </div>\n\n</div>\n', faq_html + '</div>\n', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  stamp-duty: FAQ injected.")


def patch_mortgage(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'Frequently Asked Questions' in html:
        print("  mortgage: FAQ already present, skipping.")
        return

    html = html.replace('</head>', FAQ_STYLE_SANS_DM + '</head>', 1)
    schema = build_faq_schema(MORTGAGE_FAQS, BASE_URL + "/mortgage-affordability-calculator")
    html = html.replace('</head>', schema + '</head>', 1)

    faq_html = build_faq_html_seosection(MORTGAGE_FAQS)
    html = html.replace('  </div>\n\n</div>\n', faq_html + '</div>\n', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  mortgage: FAQ injected.")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

print("Injecting FAQ sections...")
patch_thp(os.path.join(script_dir, 'take-home-pay-calculator.html'))
patch_sdlt(os.path.join(script_dir, 'stamp-duty-calculator.html'))
patch_mortgage(os.path.join(script_dir, 'mortgage-affordability-calculator.html'))
print("\nDone.")
