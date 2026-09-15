#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地预览服务器（等价于部署后的静态托管行为）

    python serve.py                 # http://127.0.0.1:8000/
    python serve.py --port 8080 --no-browser
"""
from __future__ import annotations

import argparse
import functools
import http.server
import socket
import sys
import webbrowser
from pathlib import Path


class Handler(http.server.SimpleHTTPRequestHandler):
    """支持目录式 URL（/articles/x/ -> /articles/x/index.html）和自定义 404。"""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")  # 本地改完刷新即可见
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            page = Path(self.directory) / "404.html"
            if page.is_file():
                body = page.read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):  # 精简日志
        sys.stderr.write("  " + (fmt % args) + "\n")


def _fix_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass


def pick_port(preferred: int) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0  # 交给系统分配


def main() -> int:
    _fix_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--dir", default="public", help="要托管的目录（默认 public）")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    root = (Path(__file__).resolve().parent / args.dir).resolve()
    if not (root / "index.html").is_file():
        sys.exit(f"找不到 {root / 'index.html'}\n请先运行： python build.py")

    handler = functools.partial(Handler, directory=str(root))
    port = pick_port(args.port)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"serving {root}\n  ->  {url}\n按 Ctrl+C 停止")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
