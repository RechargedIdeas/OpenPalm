"""FastAPI sidecar with server control endpoints and static GUI."""

import json
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError:
    FastAPI = None  # type: ignore

from harness_sidecar.inference.client import generate
from harness_sidecar.verify.loop import verify
from harness_sidecar.inference.models import force_cpu
import harness_sidecar.server_manager as sm

force_cpu()

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

if FastAPI is not None:
    app = FastAPI(title="Agent Harness Sidecar")

    class ChatRequest(BaseModel):
        message: str
        sources: list[str] = []
        passes: int = 2
        model: str = "phi4-mini"

    @app.post("/chat")
    def chat(req: ChatRequest) -> dict[str, Any]:
        draft = generate(req.message, req.model)
        result = verify(draft, req.sources or [req.message], req.passes)
        return {
            "draft": result["draft"],
            "claims": result["claims"],
            "passes": result["passes_run"],
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "cpu_only": "true"}

    @app.get("/control/status")
    def control_status() -> dict[str, Any]:
        return sm.status()

    @app.post("/control/start")
    def control_start() -> dict[str, Any]:
        return sm.start()

    @app.post("/control/stop")
    def control_stop() -> dict[str, Any]:
        return sm.stop()

    @app.post("/control/reset")
    def control_reset() -> dict[str, Any]:
        return sm.reset()

    def stream_chat(req: ChatRequest):
        draft = generate(req.message, req.model)
        result = verify(draft, req.sources or [req.message], req.passes)
        yield f"data: {json.dumps({'type': 'draft', 'content': result['draft']})}\n\n"
        yield f"data: {json.dumps({'type': 'claims', 'claims': result['claims']})}\n\n"

    @app.post("/chat/stream")
    def chat_stream(req: ChatRequest):
        return StreamingResponse(stream_chat(req), media_type="text/event-stream")

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        @app.get("/")
        def index():
            return FileResponse(STATIC_DIR / "index.html")
else:
    app = None
