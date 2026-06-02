#!/usr/bin/env python3
"""Release bundle entrypoint.

The normal source install starts Odysseus with `uvicorn app:app`. PyInstaller
needs an executable entrypoint, so release artifacts package this small launcher
instead of `app.py` directly.
"""

from __future__ import annotations

import os
import threading
import time
import urllib.request
import webbrowser

import uvicorn


def _open_when_ready(url: str) -> None:
    for _ in range(90):
        try:
            with urllib.request.urlopen(url, timeout=1.5):  # noqa: S310 - local URL built below
                webbrowser.open(url)
                return
        except Exception:
            time.sleep(1)


def main() -> None:
    host = os.getenv("ODYSSEUS_HOST", "127.0.0.1")
    port = int(os.getenv("ODYSSEUS_PORT", "7860"))
    url = f"http://{host}:{port}"
    if os.getenv("ODYSSEUS_OPEN_BROWSER", "1").lower() not in {"0", "false", "no", "off"}:
        threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()
    uvicorn.run("app:app", host=host, port=port)


if __name__ == "__main__":
    main()
