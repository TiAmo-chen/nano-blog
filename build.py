#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nano-blog —— 极简静态博客生成器

架构对齐 nano-ai.tech：
    Markdown  ->  markdown-it-py (GFM)  ->  Pygments(nowrap)  ->  纯静态 HTML
    零 JavaScript 运行时、零数据库、零服务端。

用法:
    pip install -r requirements.txt
    python build.py             # 生成到 public/
    python build.py --clean     # 先清空 public/ 再生成
    python serve.py             # 本地预览 http://127.0.0.1:8000/
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import re
import shutil
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

try:
    from markdown_it import MarkdownIt
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound
except ModuleNotFoundError as exc:  # pragma: no cover
    sys.exit(f"缺少依赖 {exc.name!r}，请先执行： pip install -r requirements.txt")

try:  # 可选依赖：把裸链接自动变成 <a>
    import linkify_it  # noqa: F401

    _HAS_LINKIFY = True
except ModuleNotFoundError:
    _HAS_LINKIFY = False

def _fix_console() -> None:
    """Windows 控制台默认 GBK，避免个别字符直接崩掉。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass


_fix_console()

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
THEME_DIR = ROOT / "theme"
OUT_DIR = ROOT / "public"

# ───────────────────────────── 站点配置 ─────────────────────────────
SITE = {
    "title": "橙心",                           # 站点名（标题后缀 / og:site_name）
    "tagline": "WORKLOG / NOTES / TECH",       # 首页与页脚口号
    "description": "嵌入式 / 图像算法 / AI 的工作与学习笔记",   # 默认 meta description
    "author": "橙心",
    "base_url": "https://orangeheart.top",      # ← 部署后改成自己的域名（sitemap / og:url）
    "home_headline": "记录那些真正搞明白的事。",
    "hero": "/hero.webp",                     # 首页配图；换成自己的图只需改这一行（放进 theme/ 即可）
    "hero_size": (760, 819),                   # 配图原始尺寸，写进 <img> 宽度高度防抖动
    "recent": 10,                              # 首页「最近更新」条数
}

# 首页「最近在做」卡片（可留空）
ACTIVITY: list[dict[str, str]] = [
    {
        "status": "正在进行",
        "title": "把 Obsidian 日记搬进自建博客",
        "note": "Markdown → HTML · 零 JS 运行时",
        "href": "/articles/",
        "link_text": "查看文章",
    },
]

# 首页社交链接（留空则不渲染整个区块）
SOCIALS: list[dict[str, str]] = [
    # {"label": "GitHub", "href": "https://github.com/yourname"},
    # {"label": "X", "href": "https://x.com/yourname"},
]

# 代码高亮配色：浅色 / 深色（prefers-color-scheme: dark）
PYGMENTS_LIGHT = "xcode"
PYGMENTS_DARK = "github-dark"
# ──────────────────────────────────────────────────────────────────

NAV = [("首页", "/", "home"), ("文章", "/articles/", "articles"), ("标签", "/tags/", "tags"), ("关于我", "/about/", "about")]

# ── 深/浅色切换（全站唯一的一小段内联 JS，约 20 行）────────────────────
THEME_KEY = "nano-blog-theme"
THEME_HEAD = (
    "<script>(function(){try{var t=localStorage.getItem('%s');"
    "if(t==='dark'||t==='light'){document.documentElement.dataset.theme=t}}catch(e){}})();</script>" % THEME_KEY
)
# ── 界面图标（Feather / Lucide 图标集，MIT 许可）────────────────────────
_ICON_ATTRS = (
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
)


def icon(paths: str) -> str:
    return f"<svg {_ICON_ATTRS}>{paths}</svg>"


ICON_SUN = icon(
    '<circle cx="12" cy="12" r="4"/>'
    '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2'
    'M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>'
)
ICON_MOON = icon('<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>')
ICON_UP = icon('<path d="M12 19V5"/><path d="M5 12l7-7 7 7"/>')
ICON_DOWN = icon('<path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/>')

THEME_TOGGLE = (
    '<button class="icon-btn theme-toggle" type="button" aria-label="切换日间/夜间模式" title="切换日间/夜间模式">'
    f'<span class="tt-sun">{ICON_SUN}</span><span class="tt-moon">{ICON_MOON}</span></button>'
)

# 读文章时的浮动按钮：position: fixed，不随内容滚动而消失
SCROLL_NAV = (
    '<nav class="scroll-nav" aria-label="页面滚动">'
    f'<button class="icon-btn" type="button" data-scroll="top" aria-label="回到最上面" title="回到最上面">{ICON_UP}</button>'
    f'<button class="icon-btn" type="button" data-scroll="bottom" aria-label="跳到最下面" title="跳到最下面">{ICON_DOWN}</button>'
    "</nav>"
)
THEME_SCRIPT = (
    "<script>(function(){"
    "var K='%s',b=document.querySelector('.theme-toggle');"
    "function apply(n){document.documentElement.dataset.theme=n;"
    "try{localStorage.setItem(K,n)}catch(e){}"
    "b.setAttribute('title',n==='dark'?'切换到日间模式':'切换到夜间模式')}"
    "if(b){b.addEventListener('click',function(){var c=document.documentElement.dataset.theme;"
    "if(c!=='dark'&&c!=='light'){c=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}"
    "apply(c==='dark'?'light':'dark')})}"
    "document.querySelectorAll('[data-scroll]').forEach(function(el){el.addEventListener('click',function(){"
    "window.scrollTo({top:el.getAttribute('data-scroll')==='top'?0:document.documentElement.scrollHeight,"
    "behavior:'smooth'})})});"
    "})();</script>" % THEME_KEY
)

FRONT_MATTER_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)
DATE_IN_NAME_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


# ══════════════════════════ 渲染管线 ══════════════════════════
def build_markdown() -> MarkdownIt:
    """与参考站一致：markdown-it + Pygments('nowrap')，裸代码块不带高亮包裹。"""
    return MarkdownIt("js-default", {"breaks": True, "linkify": _HAS_LINKIFY})

    # 说明：js-default = GFM 风格（表格 / 删除线），breaks=True 让单个换行也生效
    # （和 Obsidian 的阅读视图一致）。


MD = build_markdown()


def highlight_code(code: str, lang: str, _attrs: str) -> str:
    """返回空串 -> markdown-it 走默认转义渲染（即 <pre><code>…</code></pre>）。"""
    if not lang:
        return ""
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
    except ClassNotFound:
        return ""
    return highlight(code, lexer, HtmlFormatter(nowrap=True))


MD.options["highlight"] = highlight_code


def pygments_css(prefix: str) -> str:
    """生成作用域内的 Pygments 类样式，浅色默认 + 深色媒体查询。"""

    def defs(style: str) -> str:
        out = []
        for line in HtmlFormatter(style=style).get_style_defs(prefix).splitlines():
            line = line.strip()
            # 只保留 `.prefix .token {…}`，丢掉 pre / linenos / 背景块
            if line.startswith(prefix + " "):
                out.append("  " + line)
        return "\n".join(out)

    return (
        f"/* ---- Pygments · {PYGMENTS_LIGHT} ---- */\n{defs(PYGMENTS_LIGHT)}\n\n"
        f"@media (prefers-color-scheme: dark) {{\n"
        f"/* ---- Pygments · {PYGMENTS_DARK} ---- */\n{defs(PYGMENTS_DARK)}\n}}\n"
    )


# ══════════════════════════ 文章解析 ══════════════════════════
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "", text)
    return re.sub(r"-{2,}", "-", text).strip("-") or "post"


def parse_front_matter(text: str) -> tuple[dict, str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, object] = {}
    for raw in m.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
            meta[key] = [v for v in items if v]
        else:
            meta[key] = val
    return meta, text[m.end():]


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def make_summary(body: str, limit: int = 90) -> str:
    """从正文里摘一句话当 description。"""
    for block in re.split(r"\n\s*\n", body):
        text = block.strip()
        if not text or text.startswith(("#", "```", "|", ">", "---", "![")):
            continue
        text = re.sub(r"[*`_\[\]]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) >= 12:
            return text[:limit] + ("…" if len(text) > limit else "")
    return SITE["description"]


@dataclass
class Note:
    slug: str
    title: str
    date: str
    tags: list[str]
    summary: str
    words: int
    body_html: str
    source: Path

    @property
    def url(self) -> str:
        return f"/articles/{urllib.parse.quote(self.slug)}/"

    @property
    def css_url(self) -> str:
        return f"/articles/{urllib.parse.quote(self.slug)}/"

    @property
    def tag_links(self) -> str:
        return "".join(
            f'<a class="tag" href="/tags/{urllib.parse.quote(t)}/" rel="tag">{html.escape(t)}</a>'
            for t in self.tags
        )


def load_notes() -> list[Note]:
    notes: list[Note] = []
    for path in sorted(CONTENT_DIR.glob("*.md")):
        if path.name.startswith("_"):  # _about.md 之类不当作文章
            continue
        raw = path.read_text(encoding="utf-8").lstrip("\ufeff")
        meta, body = parse_front_matter(raw)

        stem = path.stem
        dm = DATE_IN_NAME_RE.search(stem)
        if meta.get("date"):
            date = str(meta["date"])
        elif dm:
            date = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
        else:
            date = dt.date.fromtimestamp(path.stat().st_mtime).isoformat()

        title = str(meta.get("title") or first_heading(body) or stem)
        if first_heading(body) == title and body.lstrip().startswith("# "):
            body = body.split("\n", 1)[1].lstrip("\n")  # 去掉重复的一级标题

        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        summary = str(meta.get("summary") or "") or make_summary(body)
        slug = slugify(str(meta.get("slug") or stem))
        notes.append(
            Note(
                slug=slug,
                title=title,
                date=date,
                tags=[str(t) for t in tags],
                summary=summary,
                words=len(re.sub(r"\s+", "", body)),
                body_html=MD.render(body).strip(),
                source=path,
            )
        )
    notes.sort(key=lambda n: (n.date, n.slug), reverse=True)
    return notes


# ══════════════════════════ 页面模板 ══════════════════════════
def asset_version(rel: str) -> str:
    """按文件内容生成短版本号，写在 <link>/<img> 后面避免浏览器/CF 用旧缓存。

    先把 CRLF 归一成 LF 再算，这样 Windows 本地构建与 Linux CI 构建得到同一个版本号。
    """
    p = THEME_DIR / rel.lstrip("/")
    if not p.is_file():
        return "0"
    data = p.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(data).hexdigest()[:8]


def versioned(url: str) -> str:
    return f"{url}?v={asset_version(url)}"


def shell(*, title: str, description: str, css: str, body: str, url: str = "/", kind: str = "website", scroll: bool = False) -> str:
    full_title = SITE["title"] if title == SITE["title"] else f"{title} · {SITE['title']}"
    base = SITE["base_url"].rstrip("/")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="author" content="{html.escape(SITE['author'])}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{versioned(css)}">
<link rel="canonical" href="{base}{url}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{html.escape(SITE['title'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{base}{url}">
<meta name="twitter:card" content="summary">
<meta name="generator" content="nano-blog · markdown-it-py + Pygments">
{THEME_HEAD}
</head>
<body>
{body}
{SCROLL_NAV if scroll else ""}
{THEME_SCRIPT}
</body>
</html>
"""


def compact_header(current: str) -> str:
    links = []
    for label, href, key in NAV:
        cur = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    return f'<header class="compact"><nav aria-label="主导航">{"".join(links)}</nav>{THEME_TOGGLE}</header>'


def footer() -> str:
    return f"<footer>{html.escape(SITE['tagline'])}</footer>"


def post_list(notes: list[Note]) -> str:
    items = []
    for n in notes:
        items.append(
            f'<li><a class="post-title" href="{n.url}">{html.escape(n.title)}</a>'
            f'<time class="post-date" datetime="{n.date}">{n.date}</time></li>'
        )
    return f'<ul class="post-list">{"".join(items)}</ul>'


def page_home(notes: list[Note]) -> str:
    recent = notes[: int(SITE["recent"])]
    hero = SITE.get("hero")
    hw, hh = SITE.get("hero_size", (720, 720))
    avatar_html = (
        f'<figure class="avatar"><img src="{versioned(hero)}" alt="" width="{hw}" height="{hh}"></figure>' if hero else ""
    )
    recent_html = "".join(
        f'<a class="recent-article-link" href="{n.url}">{html.escape(n.title)}</a>' for n in recent
    )
    activity_html = ""
    if ACTIVITY:
        cards = []
        for a in ACTIVITY:
            cards.append(
                f'<li class="timeline-item">'
                f'<span class="timeline-status">{html.escape(a.get("status", ""))}</span>'
                f'<h3>{html.escape(a.get("title", ""))}</h3>'
                f'<p>{html.escape(a.get("note", ""))}</p>'
                f'<a href="{a.get("href", "#")}">{html.escape(a.get("link_text", "查看"))} '
                f'<span aria-hidden="true">↗</span></a></li>'
            )
        activity_html = (
            '<aside class="activity" aria-labelledby="activity-title">'
            '<h2 id="activity-title">最近在做</h2>'
            f'<ol class="timeline">{"".join(cards)}</ol></aside>'
        )
    socials_html = ""
    if SOCIALS:
        lis = "".join(
            f'<li><a href="{s["href"]}" target="_blank" rel="noreferrer">{html.escape(s["label"])}</a></li>'
            for s in SOCIALS
        )
        socials_html = f'<ul class="socials" aria-label="社交账号">{lis}</ul>'

    body = f"""<main class="site">
<aside class="article-nav" aria-label="网站导航">
<nav aria-label="主导航">{"".join(f'<a href="{h}">{l}</a>' for l, h, _ in NAV)}</nav>
<section class="recent-articles" aria-labelledby="recent-title">
<h2 id="recent-title">最近更新</h2>
{recent_html}
</section>
</aside>
{activity_html}
<div class="black-world" aria-hidden="true"></div>
<div class="home-toggle">{THEME_TOGGLE}</div>
<section class="profile" aria-labelledby="profile-title">
{avatar_html}
<div class="profile-copy">
<h1 id="profile-title">{html.escape(SITE["home_headline"])}</h1>
<p>{html.escape(SITE["tagline"])}</p>
{socials_html}
</div>
</section>
<footer class="footer"><span>{html.escape(SITE["title"])}</span><span>POWERED BY NANO-BLOG</span></footer>
</main>
"""
    return shell(title=SITE["title"], description=SITE["description"], css="/styles.css", body=body, url="/")


def page_articles(notes: list[Note]) -> str:
    body = f"""<div class="site">
{compact_header("articles")}
<main>
<h1>文章</h1>
<p class="muted">共 {len(notes)} 篇 · 按时间倒序</p>
{post_list(notes)}
</main>
{footer()}
</div>
"""
    return shell(
        title="文章",
        description=f"{SITE['title']} 的全部文章，共 {len(notes)} 篇。",
        css="/articles.css",
        body=body,
        url="/articles/",
        scroll=True,
    )


def page_article(note: Note, older: Note | None, newer: Note | None) -> str:
    nav = []
    if older:
        nav.append(
            f'<a class="post-nav-link" href="{older.url}"><span>← 上一篇</span>'
            f"<strong>{html.escape(older.title)}</strong></a>"
        )
    if newer:
        nav.append(
            f'<a class="post-nav-link next" href="{newer.url}"><span>下一篇 →</span>'
            f"<strong>{html.escape(newer.title)}</strong></a>"
        )
    nav_html = f'<nav class="post-nav">{"".join(nav)}</nav>' if nav else ""
    body = f"""<div class="site">
{compact_header("articles")}
<main>
<article>
<header class="article-header">
<h1>{html.escape(note.title)}</h1>
<div class="article-meta">
<time datetime="{note.date}">{note.date}</time>
<span class="dot">·</span>
<span>{note.words:,} 字</span>
{note.tag_links}
</div>
</header>
<div class="prose">
{note.body_html}
</div>
{nav_html}
</article>
</main>
{footer()}
</div>
"""
    return shell(title=note.title, description=note.summary, css="/articles.css", body=body, url=note.url, kind="article", scroll=True)


def page_tags(tags: dict[str, list[Note]]) -> str:
    items = "".join(
        f'<li><a class="post-title" href="/tags/{urllib.parse.quote(t)}/">{html.escape(t)}</a>'
        f'<span class="post-date">{len(v)} 篇</span></li>'
        for t, v in sorted(tags.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    )
    body = f"""<div class="site">
{compact_header("tags")}
<main>
<h1>标签</h1>
<p class="muted">共 {len(tags)} 个标签</p>
<ul class="post-list">{items}</ul>
</main>
{footer()}
</div>
"""
    return shell(title="标签", description="全部标签", css="/articles.css", body=body, url="/tags/", scroll=True)


def page_tag(tag: str, notes: list[Note]) -> str:
    body = f"""<div class="site">
{compact_header("tags")}
<main>
<h1>{html.escape(tag)}</h1>
<p class="muted">共 {len(notes)} 篇文章</p>
{post_list(notes)}
</main>
{footer()}
</div>
"""
    url = f"/tags/{urllib.parse.quote(tag)}/"
    return shell(title=tag, description=f"标签「{tag}」下的文章", css="/articles.css", body=body, url=url, scroll=True)


def page_about() -> str:
    src = CONTENT_DIR / "_about.md"
    body_md = src.read_text(encoding="utf-8").lstrip("\ufeff") if src.exists() else "还没有写「关于我」。"
    body = f"""<div class="site">
{compact_header("about")}
<main>
<h1>关于我</h1>
<div class="prose">
{MD.render(body_md).strip()}
</div>
</main>
{footer()}
</div>
"""
    return shell(title="关于我", description=f"关于 {SITE['author']}", css="/articles.css", body=body, url="/about/", scroll=True)


def page_404() -> str:
    body = f"""<div class="site">
{compact_header("")}
<main>
<h1>404</h1>
<p class="muted">这个地址没有内容。</p>
<p><a href="/">← 回到首页</a></p>
</main>
{footer()}
</div>
"""
    return shell(title="404", description="页面不存在", css="/articles.css", body=body, url="/404.html")


# ══════════════════════════ 输出 ══════════════════════════
WRITTEN: set[Path] = set()


def write(rel: str, text: str) -> None:
    path = OUT_DIR / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    WRITTEN.add(path.resolve())


def copy_asset(src: Path) -> None:
    dest = OUT_DIR / src.name
    shutil.copy2(src, dest)
    WRITTEN.add(dest.resolve())


def prune() -> int:
    """删掉本次没有生成的文件（比如改了 slug 之后残留的旧页面/旧标签页）。"""
    removed = 0
    for path in [p for p in OUT_DIR.rglob("*") if p.is_file()]:
        if path.resolve() not in WRITTEN:
            path.unlink()
            removed += 1
    for path in sorted((p for p in OUT_DIR.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(path.iterdir()):
            path.rmdir()
    return removed


def build_sitemap(notes: list[Note], tags: dict[str, list[Note]]) -> str:
    base = SITE["base_url"].rstrip("/")
    urls: list[tuple[str, str]] = [("/", dt.date.today().isoformat()), ("/articles/", dt.date.today().isoformat()),
                                   ("/tags/", dt.date.today().isoformat()), ("/about/", dt.date.today().isoformat())]
    urls += [(n.url, n.date) for n in notes]
    urls += [(f"/tags/{urllib.parse.quote(t)}/", max(n.date for n in v)) for t, v in tags.items()]
    entries = "\n".join(
        f"  <url><loc>{html.escape(base + u)}</loc><lastmod>{d}</lastmod></url>" for u, d in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n'


def build_feed(notes: list[Note]) -> str:
    base = SITE["base_url"].rstrip("/")
    now = dt.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")

    def rfc822(d: str) -> str:
        try:
            return dt.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 08:00:00 +0800")
        except ValueError:
            return now

    items = "\n".join(
        "    <item>\n"
        f"      <title>{html.escape(n.title)}</title>\n"
        f"      <link>{base}{n.url}</link>\n"
        f'      <guid isPermaLink="true">{base}{n.url}</guid>\n'
        f"      <pubDate>{rfc822(n.date)}</pubDate>\n"
        f"      <description>{html.escape(n.summary)}</description>\n"
        "    </item>"
        for n in notes
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{html.escape(SITE['title'])}</title>
    <link>{base}/</link>
    <description>{html.escape(SITE['description'])}</description>
    <language>zh-cn</language>
    <lastBuildDate>{now}</lastBuildDate>
{items}
  </channel>
</rss>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="nano-blog 静态站生成器")
    ap.add_argument("--clean", action="store_true", help="生成前清空 public/")
    args = ap.parse_args()

    if not CONTENT_DIR.is_dir():
        sys.exit(f"找不到内容目录：{CONTENT_DIR}")
    if args.clean and OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    notes = load_notes()
    tags: dict[str, list[Note]] = {}
    for n in notes:
        for t in n.tags:
            tags.setdefault(t, []).append(n)

    write("index.html", page_home(notes))
    write("articles/index.html", page_articles(notes))
    for i, n in enumerate(notes):
        newer = notes[i - 1] if i > 0 else None
        older = notes[i + 1] if i + 1 < len(notes) else None
        write(f"articles/{n.slug}/index.html", page_article(n, older, newer))
    write("tags/index.html", page_tags(tags))
    for t, items in tags.items():
        write(f"tags/{t}/index.html", page_tag(t, items))
    write("about/index.html", page_about())
    write("404.html", page_404())
    write("sitemap.xml", build_sitemap(notes, tags))
    write("feed.xml", build_feed(notes))
    write(
        "robots.txt",
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['base_url'].rstrip('/')}/sitemap.xml\n",
    )

    # 样式与静态资源
    write("styles.css", (THEME_DIR / "styles.css").read_text(encoding="utf-8"))
    articles_css = (THEME_DIR / "articles.css").read_text(encoding="utf-8")
    articles_css += "\n" + pygments_css(".prose .language-python")
    write("articles.css", articles_css)
    for asset in THEME_DIR.iterdir():
        if asset.is_dir():  # 主题子目录整体拷贝（如 theme/image/**）
            for f in asset.rglob("*"):
                if f.is_file():
                    dest = OUT_DIR / f.relative_to(THEME_DIR)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    WRITTEN.add(dest.resolve())
        elif asset.suffix in {".svg", ".png", ".webp", ".ico", ".jpg", ".woff2"} or asset.name == "CNAME":
            copy_asset(asset)

    stale = prune()
    total = sum(f.stat().st_size for f in OUT_DIR.rglob("*") if f.is_file())
    pages = len(list(OUT_DIR.rglob("*.html")))
    print(f"[ok] 构建完成：{pages} 个页面 / {total / 1024:.0f} KB -> {OUT_DIR}")
    if stale:
        print(f"  清理了 {stale} 个过期文件（public/ 里没有本次生成记录的）")
    print(f"  文章 {len(notes)} 篇 · 标签 {len(tags)} 个")
    for n in notes:
        print(f"    {n.date}  {n.title}  ({n.words:,} 字)")
    if SITE["base_url"].endswith("example.com"):
        print("  提示：SITE['base_url'] 还是 example.com，部署前记得改。")
    if not _HAS_LINKIFY:
        print("  提示：未安装 linkify-it-py，正文里的裸链接不会变成超链接。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
