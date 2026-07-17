#!/usr/bin/env python3
"""ビュワー（viewer/index.html）をローカルHTTPサーバーで開く。

ビュワーは data/output/places.json を fetch() で参照するため、
ブラウザの制約により file:// では動かない。このスクリプトが配信する。

使い方:
    uv run python scripts/serve_viewer.py                # 自分だけ（127.0.0.1:8765）
    uv run python scripts/serve_viewer.py 8055 --share   # 他メンバーに共有（0.0.0.0:8055）

セキュリティ: 配信するのは /viewer/ と /data/output/places.json のみ。
それ以外（.env・.git・data/raw 等）へのアクセスは 403 で拒否する。
"""
import functools
import http.server
import socket
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_FILES = {"/viewer/", "/viewer/index.html", "/data/output/places.json"}
REDIRECTS = {"": "/viewer/", "/": "/viewer/", "/viewer": "/viewer/"}


class RestrictedHandler(http.server.SimpleHTTPRequestHandler):
    """許可リスト方式のハンドラ。リポジトリ内の他ファイル（シークレット等）を配信しない。"""

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in REDIRECTS:
            self.send_response(301)
            self.send_header("Location", REDIRECTS[path])
            self.end_headers()
            return None
        if path not in ALLOWED_FILES:
            # 注意: ステータス行はASCII限定のため英語（このサーバーはビュワーとplaces.jsonのみ配信する）
            self.send_error(403, "Forbidden", "This server only serves /viewer/ and places.json")
            return None
        return super().send_head()


def lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # 実際には送信しない（経路のIPを知るだけ）
            return s.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())


def main():
    args = [a for a in sys.argv[1:]]
    share = "--share" in args
    ports = [a for a in args if a.isdigit()]
    port = int(ports[0]) if ports else 8765
    host = "0.0.0.0" if share else "127.0.0.1"

    handler = functools.partial(RestrictedHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer((host, port), handler)

    local_url = f"http://localhost:{port}/viewer/"
    print(f"ビュワーを配信中: {local_url} （Ctrl+C で終了）")
    if share:
        print(f"共有URL（同一ネットワークのメンバー向け）: http://{lan_ip()}:{port}/viewer/")
        print("※配信は /viewer/ と /data/output/places.json のみ。他のパスは403で拒否します")
    threading.Timer(0.3, lambda: webbrowser.open(local_url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n終了しました")


if __name__ == "__main__":
    main()
