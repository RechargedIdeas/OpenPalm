#!/usr/bin/env python3
"""Python GUI launcher with complete parity. Auto-starts the sidecar and opens the web GUI."""

import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness_sidecar import server_manager as sm


def main() -> None:
    print("Agent Harness — Python GUI (CPU-only)")
    st = sm.status()
    if not st["running"]:
        print("Server not running. Starting…")
        result = sm.start()
        print(result)
        time.sleep(1.2)
    else:
        print(f"Server already running (pid {st['pid']})")

    url = "http://127.0.0.1:8765/"
    print(f"Opening GUI at {url}")
    print("Use Start / Stop / Reset in the header to manage the server.")
    print("Press Ctrl+C to exit this launcher (server keeps running unless you Stop it).")
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLauncher exiting. Server status:", sm.status())


if __name__ == "__main__":
    main()
