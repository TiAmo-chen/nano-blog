#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Obsidian / 任意 Markdown 笔记导入 content/，自动补 front matter。

用法:
    python tools/import_note.py "D:\\Obsidian\\...\\2026-09-10.md" \
        --title "S1100+ 课程分享：真正的计算机素养是什么" \
        --tags 计算机基础,学习笔记 \
        --slug computer-literacy

不传 --title 时用正文第一个 "# 标题" 或文件名；不传 --slug 时用文件名推导。
已存在的 front matter 会被保留，只补缺失字段。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

def _fix_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass


_fix_console()

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
CONTENT_DIR = ROOT / "content"

FRONT_MATTER_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)
DATE_IN_NAME_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "", text)
    return re.sub(r"-{2,}", "-", text).strip("-") or "post"


def main() -> int:
    ap = argparse.ArgumentParser(description="导入 Markdown 笔记到 content/")
    ap.add_argument("source", help="源 Markdown 文件")
    ap.add_argument("--title")
    ap.add_argument("--tags", default="", help="逗号分隔，例如：AI,提示词")
    ap.add_argument("--slug")
    ap.add_argument("--date", help="YYYY-MM-DD，默认从文件名或文件时间取")
    ap.add_argument("--summary", default="")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    src = Path(args.source).expanduser()
    if not src.is_file():
        sys.exit(f"找不到源文件：{src}")

    raw = src.read_text(encoding="utf-8").lstrip("\ufeff")
    existing_meta: dict[str, str] = {}
    m = FRONT_MATTER_RE.match(raw)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                existing_meta[k.strip()] = v.strip()
        body = raw[m.end():]
    else:
        body = raw

    dm = DATE_IN_NAME_RE.search(src.stem)
    date = args.date or existing_meta.get("date") or (f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}" if dm else
                                                     dt.date.fromtimestamp(src.stat().st_mtime).isoformat())

    title = args.title or existing_meta.get("title")
    if not title:
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    title = title or src.stem

    slug = slugify(args.slug or existing_meta.get("slug") or src.stem)
    tags = [t.strip() for t in (args.tags or existing_meta.get("tags", "").strip("[]")).split(",") if t.strip()]
    tail = body.lstrip("\n")
    if tail.startswith(f"# {title}"):
        tail = tail.split("\n", 1)[1].lstrip("\n")  # 标题已进 front matter，正文去掉重复 H1

    fm = ["---", f"title: {title}", f"date: {date}", f"tags: [{', '.join(tags)}]"]
    if args.summary:
        fm.append(f"summary: {args.summary}")
    fm += [f"slug: {slug}", "---", ""]

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    dest = CONTENT_DIR / f"{slug}.md"
    if dest.exists() and not args.overwrite:
        sys.exit(f"目标已存在：{dest}（加 --overwrite 覆盖）")
    dest.write_text("\n".join(fm) + tail, encoding="utf-8", newline="\n")

    print(f"[ok] {src.name}  ->  {dest}")
    print(f"   title: {title}\n   date: {date}\n   tags: {tags or '（无）'}\n   slug: {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
