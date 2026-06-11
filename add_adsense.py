#!/usr/bin/env python3
"""Insert Google AdSense script tag after the viewport meta tag in every HTML file."""
import os
import glob

ADSENSE_SNIPPET = (
    '  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3649044515825371"\n'
    '       crossorigin="anonymous"></script>\n'
)
MARKER = 'ca-pub-3649044515825371'
VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'

base = os.path.dirname(os.path.abspath(__file__))
html_files = sorted(glob.glob(os.path.join(base, '**', '*.html'), recursive=True))

updated = []
skipped_already_has = []
skipped_no_viewport = []

for path in html_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if MARKER in content:
        skipped_already_has.append(os.path.basename(path))
        continue

    if VIEWPORT_TAG not in content:
        skipped_no_viewport.append(os.path.basename(path))
        print(f'WARNING: no viewport tag found in {os.path.basename(path)} — skipped')
        continue

    new_content = content.replace(
        VIEWPORT_TAG + '\n',
        VIEWPORT_TAG + '\n' + ADSENSE_SNIPPET,
        1
    )

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    updated.append(os.path.basename(path))

print(f'\nUpdated ({len(updated)} files):')
for f in updated:
    print(f'  + {f}')

if skipped_already_has:
    print(f'\nSkipped — already had AdSense ({len(skipped_already_has)}):')
    for f in skipped_already_has:
        print(f'  ~ {f}')

if skipped_no_viewport:
    print(f'\nSkipped — no viewport tag ({len(skipped_no_viewport)}):')
    for f in skipped_no_viewport:
        print(f'  ! {f}')

print(f'\nDone. {len(updated)} files updated.')
