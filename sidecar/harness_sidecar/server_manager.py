"""Process manager for the sidecar. Start, stop, reset, status."""

import os
import signal
import subprocess
import time
from pathlib import Path

PID_FILE = Path("/tmp/agent-harness-sidecar.pid")
LOG_FILE = Path("/tmp/agent-harness-sidecar.log")
HOST = "127.0.0.1"
PORT = 8765


def is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        PID_FILE.unlink(missing_ok=True)
        return False


def start() -> dict:
    if is_running():
        return {"ok": True, "status": "already_running", "pid": int(PID_FILE.read_text())}
    env = os.environ.copy()
    env["OLLAMA_VULKAN"] = "0"
    cmd = [
        "python3", "-m", "uvicorn",
        "harness_sidecar.api.server:app",
        "--host", HOST,
        "--port", str(PORT),
    ]
    log = open(LOG_FILE, "a")
    proc = subprocess.Popen(
        cmd,
        cwd=str(Path(__file__).resolve().parents[1]),
        env=env,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid))
    time.sleep(0.8)
    return {"ok": is_running(), "status": "started", "pid": proc.pid}


def stop() -> dict:
    if not is_running():
        return {"ok": True, "status": "not_running"}
    pid = int(PID_FILE.read_text())
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        if is_running():
            os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    PID_FILE.unlink(missing_ok=True)
    return {"ok": True, "status": "stopped"}


def reset() -> dict:
    stop()
    time.sleep(0.3)
    return start()


def status() -> dict:
    running = is_running()
    return {
        "running": running,
        "pid": int(PID_FILE.read_text()) if running else None,
        "url": f"http://{HOST}:{PORT}",
        "cpu_only": True,
    }
