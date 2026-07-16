"""プロジェクト直下の .env を読み込んで os.environ に反映する小さなローダー。
（python-dotenvを入れるほどでもないため自前。書式: KEY=VALUE、#始まりはコメント）

使い方:
    import envfile; envfile.load()
"""
import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def load(path: Path = ENV_PATH, override: bool = False) -> dict:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        values[key] = val
        if override or key not in os.environ:
            os.environ[key] = val
    return values


def require(*keys: str) -> None:
    load()
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        raise SystemExit(
            f"環境変数が未設定です: {', '.join(missing)}\n"
            f".env.example を .env にコピーして値を記入してください（{ENV_PATH}）")
