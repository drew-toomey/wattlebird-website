#!/usr/bin/env python3
"""Build the dev blog from blog/<slug>/post.md into static pages (no build step on GitHub Pages).

Usage: python3 tools/build_blog.py      then: node tools/og_cards.js   (makes the 1200x630 share cards)
Each post folder blog/<slug>/: post.md (front matter: title, slug, issue, date YYYY-MM-DD, author, summary, cover, cover_alt,
optional draft: true) and its JPG images. Writes blog/<slug>/index.html, blog/index.html, blog/feed.xml and the
home page "From the shop floor" strip between the BLOG markers in index.html. Drafts are skipped.
"""
import html, re, os, shutil, datetime, yaml
from email.utils import format_datetime
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(ROOT, "blog"); SITE = "https://wattlebirdgames.com"
E = html.escape

def inline(t):
    t = E(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", lambda m: f'<a href="{E(m[2])}">{m[1]}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<i>\1</i>", t)

def body_html(md):
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        b = block.strip()
        m = re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)(?:\n(.+))?", b, re.S)
        if m:
            cap = m[3] or m[1]
            out.append(f'<figure><img src="{E(m[2])}" alt="{E(m[1])}" loading="lazy"><figcaption>{inline(cap.strip())}</figcaption></figure>')
        elif b.startswith("## "):
            out.append(f"<h2>{inline(b[3:])}</h2>")
        elif all(l.lstrip().startswith(("- ", "* ")) for l in b.splitlines()):
            out.append("<ul>" + "".join(f"<li>{inline(l.lstrip()[2:])}</li>" for l in b.splitlines()) + "</ul>")
        else:
            out.append(f"<p>{inline(' '.join(b.splitlines()))}</p>")
    return "\n".join(out)

def load():
    posts = []
    for slug in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, slug, "post.md")
        if not os.path.isfile(p):
            continue
        raw = open(p, encoding="utf-8").read()
        _, fm, md = raw.split("---", 2)
        meta = yaml.safe_load(fm)
        if meta.get("draft"):
            continue
        meta["slug"], meta["md"], meta["dir"] = slug, md, os.path.dirname(p)
        meta["date"] = datetime.date.fromisoformat(str(meta["date"]))
        posts.append(meta)
    return sorted(posts, key=lambda m: (m["date"], m["slug"]), reverse=True)

def nice(d):
    return f"{d.day} {d.strftime('%B %Y')}"

def card(m, prefix):
    return (f'<a class="post-card" href="{prefix}{m["slug"]}/"><div class="pc-img"><img src="{prefix}{m["slug"]}/{m["cover"]}" alt="" loading="lazy">'
            f'<span class="issue">ISSUE #{E(str(m["issue"]))}</span></div><div class="pc-t"><h3>{E(m["title"])}</h3>'
            f'<p>{nice(m["date"])} · {E(m["author"])}</p><p class="sum">{E(m["summary"])}</p></div></a>')

def shell(depth, title, desc, url, og, body, kind="website"):
    home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    head, rest = home.split("<body>", 1)
    nav = "<nav" + rest.split("<nav", 1)[1].split("</nav>", 1)[0] + "</nav>"
    foot = "<footer>" + rest.split("<footer>", 1)[1]
    p = "../" * depth
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(title)}"><meta property="og:type" content="{kind}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{url}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', head)
    head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{og}">', head)
    fix = lambda s: re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]*)"', lambda m: f'{m[1]}="{p}{m[2]}"', s)
    nav = fix(nav).replace(f'href="{p}#', f'href="{p}index.html#')
    return fix(head) + "<body>\n" + nav + f'\n<main class="hero blogpage">{body}</main>\n' + fix(foot)

def main():
    posts = load()
    for m in posts:
        d = os.path.join(OUT, m["slug"]); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):  # keep images web-sized (1600 px wide max)
            if f.lower().endswith((".jpg", ".jpeg", ".png")) and f != "card.jpg":
                fp = os.path.join(d, f); im = Image.open(fp)
                if im.width > 1600:
                    im.convert("RGB").resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS).save(fp, quality=84, optimize=True)
        words = len(re.findall(r"\w+", m["md"]))
        url = f"{SITE}/blog/{m['slug']}/"
        share = (f'<div class="share">SHARE: <a href="#" data-copy="{url}">Copy link</a>'
                 f'<a href="https://bsky.app/intent/compose?text={E(m["title"])}%20{url}" target="_blank" rel="noopener">Bluesky</a>'
                 f'<a href="https://www.reddit.com/submit?url={url}&amp;title={E(m["title"])}" target="_blank" rel="noopener">Reddit</a></div>')
        body = (f'<div class="page-top"><article class="post"><span class="issue">ISSUE #{E(str(m["issue"]))}</span><h1>{E(m["title"])}</h1>'
                f'<div class="meta">{nice(m["date"])} · By {E(m["author"])} · {max(1, round(words / 200))} min read</div>'
                f'{body_html(m["md"])}{share}</article>'
                f'<div class="post-cta"><div><b>Play it early</b><br>Become a playtester and get named in the credits.</div>'
                f'<div class="btns"><a class="btn" href="https://docs.google.com/forms/d/e/1FAIpQLSfuAGHpLEdJkSr7bj7zB9c6hjdYOWPPjjxjx5vicbKO80FxpA/viewform" target="_blank" rel="noopener">Become a playtester</a></div></div>'
                f'<div class="navpost"><a href="../">&larr; All posts</a></div></div>')
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            shell(2, f'{m["title"]} · Wattlebird Games', m["summary"], url, f"{url}card.jpg", body, "article"))
    lst = ('<div class="wide page-top"><div class="sec-head"><h2>Dev blog</h2><a class="rss" href="feed.xml">RSS feed</a></div>'
           '<p class="lead">News from the shop floor: what we\'re building, what we changed, and why.</p>'
           '<div class="posts">' + "".join(card(m, "") for m in posts) + "</div></div>")
    og = f"{SITE}/blog/{posts[0]['slug']}/card.jpg" if posts else f"{SITE}/img/og-comic-corner.jpg"
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell(1, "Dev blog · Wattlebird Games", "News from the Comic Corner shop floor.", f"{SITE}/blog/", og, lst))
    items = "".join(
        f'<item><title>{E(m["title"])}</title><link>{SITE}/blog/{m["slug"]}/</link><guid>{SITE}/blog/{m["slug"]}/</guid>'
        f'<pubDate>{format_datetime(datetime.datetime.combine(m["date"], datetime.time(9), datetime.timezone(datetime.timedelta(hours=11))))}</pubDate>'
        f'<description>{E(m["summary"])}</description></item>' for m in posts)
    open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Wattlebird Games dev blog</title>'
        f'<link>{SITE}/blog/</link><description>News from the Comic Corner shop floor.</description><language>en-au</language>{items}</channel></rss>\n')
    home_p = os.path.join(ROOT, "index.html")
    home = open(home_p, encoding="utf-8").read()
    strip = ("" if not posts else
             '<section class="cream blogsec" id="blog"><div class="wide"><div class="sec-head"><h2>From the shop floor</h2>'
             '<a class="more" href="blog/">All posts &rarr;</a></div><p class="lead">Our dev blog. Short updates on Comic Corner as it grows.</p>'
             '<div class="posts">' + "".join(card(m, "blog/") for m in posts[:3]) + "</div></div></section>")
    home = re.sub(r"<!--BLOG:START-->.*?<!--BLOG:END-->", lambda _: f"<!--BLOG:START-->{strip}<!--BLOG:END-->", home, flags=re.S)
    open(home_p, "w", encoding="utf-8").write(home)
    print(f"built {len(posts)} post(s):", ", ".join(m["slug"] for m in posts))

if __name__ == "__main__":
    main()
