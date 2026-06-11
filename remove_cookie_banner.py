#!/usr/bin/env python3
"""Remove the custom cookie consent banner (div + script) from every HTML page.

The banner always appears as:
  <div id="cookie-banner" ...>...</div>
  <script>
    [acceptCookies / declineCookies / IIFE]
  </script>
  </body>
</html>

We match from the opening <div id="cookie-banner" to the </script> immediately
before </body> and remove the entire block. The cookies.html article content
(which references cookie_consent in prose) is untouched.
"""
import os
import re
import glob

PATTERN = re.compile(
    r'\n<div id="cookie-banner".*?</script>\n*(?=</body>)',
    re.DOTALL
)

base = os.path.dirname(os.path.abspath(__file__))
html_files = sorted(glob.glob(os.path.join(base, '**', '*.html'), recursive=True))

updated = []
skipped = []

for path in html_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'id="cookie-banner"' not in content:
        skipped.append(os.path.basename(path))
        continue

    new_content, count = PATTERN.subn('', content)

    if count == 0:
        print(f'WARNING: pattern not matched in {os.path.basename(path)} — skipped')
        skipped.append(os.path.basename(path))
        continue

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    updated.append(os.path.basename(path))
    print(f'  cleaned {os.path.basename(path)} ({count} block removed)')

print(f'\nUpdated: {len(updated)} files')
print(f'Skipped: {len(skipped)} files ({", ".join(skipped) if skipped else "none"})')
