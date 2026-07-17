#!/usr/bin/env python3
"""ビュワー（viewer/index.html）をローカルHTTPサーバーで開く。

ビュワーは data/output/places.json を fetch() で参照するため、
ブラウザの制約により file:// では動かない。このスクリプトがリポジトリを
ローカルHTTPで配信し、既定ブラウザで自動的に開く（Ctrl+C で終了）。

使い方: uv run python scripts/serve_viewer.py [ポート番号(既定8765)]
"""
import functools
import http.server
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    url = f"http://localhost:{PORT}/viewer/"
    print(f"ビュワーを配信中: {url} （Ctrl+C で終了）")
    threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n終了しました")


if __name__ == "__main__":
    main()
