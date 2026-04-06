#!/usr/bin/env python3
"""
build.py - Convert posts/*.org to HTML and regenerate blog.html

Usage:
    python build.py          # build all posts
    python build.py --dry    # preview what would be built

Post format (posts/my-post.org):
    #+TITLE: My Post Title
    #+DATE: 2026-04-06
    #+DESCRIPTION: One-line summary shown on blog index

    Content here...
"""

import re
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def _find_pandoc():
    p = shutil.which('pandoc')
    if p:
        return p
    for candidate in ['/opt/homebrew/bin/pandoc', '/usr/local/bin/pandoc']:
        if Path(candidate).exists():
            return candidate
    sys.exit("Error: pandoc not found. Install with: brew install pandoc")

SITE_ROOT = Path(__file__).parent


_NAV = """\
<nav>
<a href="index.html" class="nav-name">Calceit</a>
<div class="nav-links">
<a href="cv.html">CV</a>
<a href="projects.html">Projects</a>
<a href="blog.html" class="active">Blog</a>
<a href="Aryan_Sahu_Resume.pdf" target="_blank" class="nav-btn">Resume ↓</a>
</div>
</nav>"""

_FOOTER = """\
<footer>

<div class="footer-top">

<div class="footer-links">
<a href="https://github.com/calceit" target="_blank" aria-label="GitHub">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
</a>
<a href="https://linkedin.com/in/aryan-s4hu/" target="_blank" aria-label="LinkedIn">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
</a>
<a href="mailto:aryan_sahu@outlook.com" aria-label="Email">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
</a>
</div>

<div class="footer-extra">
Also check out: <a href="https://carsithinkabout.com" target="_blank">carsithinkabout.com</a>!
</div>

</div>

<div class="footer-copy">
Aryan Sahu · calceit.com
</div>

</footer>"""


def parse_org_meta(text):
    meta = {}
    for line in text.splitlines():
        m = re.match(r'^#\+(\w+):\s*(.+)', line)
        if m:
            meta[m.group(1).upper()] = m.group(2).strip()
    return meta


def org_to_html(org_file):
    result = subprocess.run(
        [_find_pandoc(), '-f', 'org', '-t', 'html', '--no-highlight', str(org_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR (pandoc): {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def fmt_date(date_str):
    """'2026-04-06' → 'Apr 2026'"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %Y')
    except ValueError:
        return date_str


def build_post(org_file, dry=False):
    text = org_file.read_text()
    meta = parse_org_meta(text)

    title = meta.get('TITLE', org_file.stem)
    date_raw = meta.get('DATE', '')
    description = meta.get('DESCRIPTION', '')
    slug = org_file.stem
    out_path = SITE_ROOT / f"{slug}.html"
    date_display = fmt_date(date_raw) if date_raw else ''

    if dry:
        print(f"  [dry] {org_file.name} → {out_path.name}  ({title!r})")
        return {'title': title, 'slug': slug, 'date_raw': date_raw,
                'date_display': date_display, 'description': description,
                'url': f"{slug}.html"}

    body = org_to_html(org_file)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Aryan Sahu</title>
<link rel="stylesheet" href="style.css">
</head>

<body>

{_NAV}

<main>

<h1>{title}</h1>
{f'<p class="post-date">{date_display}</p>' if date_display else ''}

{body}
</main>

{_FOOTER}

</body>
</html>
"""

    out_path.write_text(html)
    print(f"  {org_file.name} → {out_path.name}")

    return {'title': title, 'slug': slug, 'date_raw': date_raw,
            'date_display': date_display, 'description': description,
            'url': f"{slug}.html"}



def regenerate_blog_index(posts, dry=False):
    posts_sorted = sorted(posts, key=lambda p: p['date_raw'], reverse=True)

    articles = ''
    for p in posts_sorted:
        desc = f'\n<p>{p["description"]}</p>' if p['description'] else ''
        articles += f"""
<article class="note">
<div class="note-date">{p["date_display"]}</div>
<h2 class="note-title"><a href="{p["url"]}">{p["title"]}</a></h2>{desc}
</article>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog | Aryan Sahu</title>
<link rel="stylesheet" href="style.css">
</head>

<body>

<nav>
<a href="index.html" class="nav-name">Calceit</a>
<div class="nav-links">
<a href="cv.html">CV</a>
<a href="projects.html">Projects</a>
<a href="blog.html" class="active">Blog</a>
<a href="Aryan_Sahu_Resume.pdf" target="_blank" class="nav-btn">Resume ↓</a>
</div>
</nav>

<main>

<h1 class="page-title">Blog</h1>

<p class="page-sub">
Notes, things I've figured out, and occasional longer writeups.
</p>

<div class="blog-list">
{articles}
</div>

</main>

{_FOOTER}

</body>
</html>
"""

    n = len(posts_sorted)
    if dry:
        print(f"  [dry] blog.html ← {n} post{'s' if n != 1 else ''}")
        return

    (SITE_ROOT / 'blog.html').write_text(html)
    print(f"  blog.html regenerated ({n} post{'s' if n != 1 else ''})")



def main():
    dry = '--dry' in sys.argv

    posts_dir = SITE_ROOT / 'posts'
    org_files = sorted(posts_dir.glob('*.org'))

    if not org_files:
        print("No .org files found in posts/")
        sys.exit(0)

    n = len(org_files)
    print(f"{'[dry run] ' if dry else ''}Building {n} post{'s' if n != 1 else ''}...")

    posts = [build_post(f, dry=dry) for f in org_files]
    regenerate_blog_index(posts, dry=dry)

    print("Done.")


if __name__ == '__main__':
    main()
