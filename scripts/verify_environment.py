"""Print reproducible environment and embedding-backend evidence."""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import LocalEmbedder  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload: dict[str, object] = {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "virtual_environment": sys.prefix != sys.base_prefix,
    }
    try:
        embedder = LocalEmbedder()
        vector = embedder("Kiểm tra embedding tiếng Việt")
        payload.update(
            {
                "requested_backend": "local",
                "actual_backend": embedder._backend_name,
                "model": embedder.model_name,
                "vector_dimension": len(vector),
                "fallback": False,
            }
        )
    except Exception as error:
        payload.update(
            {
                "requested_backend": "local",
                "actual_backend": None,
                "fallback": True,
                "fallback_reason": f"{type(error).__name__}: {error}",
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
