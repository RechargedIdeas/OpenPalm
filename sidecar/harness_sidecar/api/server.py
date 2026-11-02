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
from harness_sidecar.data import store as data_store
from harness_sidecar import pairing

force_cpu()

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

if FastAPI is not None:
    app = FastAPI(title="OpenPalm Sidecar")

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


    @app.get("/data")
    def data_get() -> dict[str, Any]:
        return data_store.load()

    @app.put("/data/messages")
    def data_messages(body: dict[str, Any]) -> dict[str, Any]:
        msgs = body.get("messages", [])
        data_store.set_messages(msgs)
        return {"ok": True, "count": len(msgs)}

    @app.put("/data/settings")
    def data_settings(body: dict[str, Any]) -> dict[str, Any]:
        data_store.set_settings(body)
        return {"ok": True, "settings": data_store.get_settings()}

    @app.put("/data/sources")
    def data_sources(body: dict[str, Any]) -> dict[str, Any]:
        src = body.get("sources", "")
        data_store.set_sources(src)
        return {"ok": True}


    @app.get("/pair/code")
    def pair_code() -> dict[str, Any]:
        return pairing.create_code()

    @app.post("/pair/redeem")
    def pair_redeem(body: dict[str, Any]) -> dict[str, Any]:
        code = body.get("code", "")
        result = pairing.redeem(code)
        if not result:
            return {"ok": False, "error": "invalid or expired code"}
        return result

    @app.get("/pair/status")
    def pair_status() -> dict[str, Any]:
        return pairing.status()


    @app.get("/models")
    def list_models() -> dict[str, Any]:
        from harness_sidecar.framework.models.router import ModelRouter
        from harness_sidecar.inference.client import generate
        r = ModelRouter(generate)
        return {"specialists": r.list()}

    @app.post("/specialist/{name}")
    def run_specialist(name: str, body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.models.router import ModelRouter
        from harness_sidecar.inference.client import generate
        r = ModelRouter(generate)
        return r.run(name, body.get("prompt", ""), body.get("model"))

    @app.post("/acp")
    def acp_endpoint(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.protocols.acp import ACPHandler
        if not hasattr(app.state, "acp"):
            app.state.acp = ACPHandler()
        return app.state.acp.handle(body)

    @app.get("/snapshots")
    def list_snapshots() -> dict[str, Any]:
        from harness_sidecar.framework.resilience.snapshot import SnapshotStore
        return {"snapshots": SnapshotStore().list()}

    @app.post("/snapshot")
    def take_snapshot(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.resilience.snapshot import SnapshotStore
        sid = SnapshotStore().take(body.get("state", {}), body.get("label", ""))
        return {"id": sid}


    @app.post("/rama")
    def rama_run(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.rama.router import RAMA
        from harness_sidecar.inference.client import generate
        r = RAMA(generate)
        return r.run(body.get("prompt", ""), body.get("mode", "auto"))

    @app.get("/telemetry")
    def telemetry() -> dict[str, Any]:
        from harness_sidecar.framework.ml.telemetry.stream import ThoughtStream
        # Shared stream would be app.state in production
        return {"note": "attach ThoughtStream to app.state for live view"}

    @app.post("/ml/build")
    def ml_build(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder, ModelSpec
        b = ModelBuilder()
        spec = ModelSpec(
            name=body.get("name", "custom"),
            domain=body.get("domain", "general"),
            system_prompt=body.get("system_prompt", "You are a helpful assistant."),
            examples=body.get("examples", []),
        )
        return b.build(spec)

    @app.post("/ml/train")
    def ml_train(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder
        return ModelBuilder().train(body.get("name", ""), body.get("epochs", 1))


    @app.post("/rama/feedback")
    def rama_feedback(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.rama.router import RAMA
        from harness_sidecar.inference.client import generate
        if not hasattr(app.state, "rama"):
            app.state.rama = RAMA(generate)
        return app.state.rama.add_feedback(
            body.get("prompt", ""),
            body.get("output", ""),
            int(body.get("rating", 3)),
            body.get("note", ""),
        )

    @app.get("/rama/versions")
    def rama_versions() -> dict[str, Any]:
        from harness_sidecar.framework.ml.rama.router import RAMA
        from harness_sidecar.inference.client import generate
        if not hasattr(app.state, "rama"):
            app.state.rama = RAMA(generate)
        return {"versions": app.state.rama.list_versions()}

    @app.post("/rama/rollback")
    def rama_rollback(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.rama.router import RAMA
        from harness_sidecar.inference.client import generate
        if not hasattr(app.state, "rama"):
            app.state.rama = RAMA(generate)
        ok = app.state.rama.rollback(body.get("id"))
        return {"ok": ok, "versions": app.state.rama.list_versions()}


    @app.get("/train/status")
    def train_status() -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        return {
            "telemetry": app.state.pipeline.telemetry_enabled,
            "jobs": app.state.pipeline.list_jobs(),
            "active": app.state.pipeline.active(),
            "samples": len(app.state.pipeline.telemetry),
        }

    @app.post("/train/telemetry")
    def train_telemetry(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        app.state.pipeline.set_telemetry(bool(body.get("enabled", False)))
        return {"telemetry": app.state.pipeline.telemetry_enabled}

    @app.post("/train/self")
    def train_self() -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        if not hasattr(app.state, "rama"):
            from harness_sidecar.framework.ml.rama.router import RAMA
            from harness_sidecar.inference.client import generate
            app.state.rama = RAMA(generate)
        jid = app.state.pipeline.start_self_train(app.state.rama)
        return {"job": jid}

    @app.post("/train/manual")
    def train_manual(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        if not hasattr(app.state, "rama"):
            from harness_sidecar.framework.ml.rama.router import RAMA
            from harness_sidecar.inference.client import generate
            app.state.rama = RAMA(generate)
        jid = app.state.pipeline.start_manual(
            app.state.rama, body.get("prompt", ""), body.get("specialist", "tooluse")
        )
        return {"job": jid}

    @app.post("/train/ml")
    def train_ml(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder
        if not hasattr(app.state, "builder"):
            app.state.builder = ModelBuilder()
        jid = app.state.pipeline.start_ml(
            app.state.builder, body.get("name", ""), int(body.get("epochs", 1))
        )
        return {"job": jid}

    @app.get("/train/job/{jid}")
    def train_job(jid: str) -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            return {"error": "no pipeline"}
        s = app.state.pipeline.status(jid)
        return s or {"error": "not found"}


    @app.get("/hardware")
    def hardware() -> dict[str, Any]:
        from harness_sidecar.framework.hardware import detect, apply
        prof = detect()
        apply(prof)
        return {
            "cpu_count": prof.cpu_count,
            "gpu_count": prof.gpu_count,
            "gpu_names": prof.gpu_names,
            "gpus": [{"index": g.index, "name": g.name, "backend": g.backend, "memory_mb": g.memory_mb, "vendor": g.vendor} for g in prof.gpus],
            "memory_gb": prof.memory_gb,
            "mode": prof.mode,
            "backend": prof.backend,
            "workers": prof.workers,
            "batch_size": prof.batch_size,
            "unified_memory": prof.unified_memory,
            "gpu_memory_fraction": prof.gpu_memory_fraction,
        }

    @app.get("/models/list")
    def models_list() -> dict[str, Any]:
        from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder
        if not hasattr(app.state, "builder"):
            app.state.builder = ModelBuilder()
        names = app.state.builder.list()
        return {"models": [app.state.builder.info(n) for n in names]}

    @app.delete("/models/{name}")
    def models_delete(name: str) -> dict[str, Any]:
        from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder
        if not hasattr(app.state, "builder"):
            app.state.builder = ModelBuilder()
        ok = app.state.builder.delete(name)
        return {"ok": ok}

    @app.post("/train/config")
    def train_config(body: dict[str, Any]) -> dict[str, Any]:
        """Set workers/batch override for the session."""
        if not hasattr(app.state, "train_config"):
            app.state.train_config = {}
        if "workers" in body:
            app.state.train_config["workers"] = int(body["workers"])
        if "batch_size" in body:
            app.state.train_config["batch_size"] = int(body["batch_size"])
        return app.state.train_config


    @app.post("/hardware/bench")
    def hardware_bench() -> dict[str, Any]:
        from harness_sidecar.framework.hardware_bench import benchmark, apply_bench
        result = benchmark()
        apply_bench(result)
        return {
            "cpu_score": result.cpu_score,
            "gpu_score": result.gpu_score,
            "recommended_workers": result.recommended_workers,
            "recommended_batch": result.recommended_batch,
            "duration_ms": result.duration_ms,
            "notes": result.notes,
        }


    @app.post("/hardware/optimize")
    def hardware_optimize() -> dict[str, Any]:
        from harness_sidecar.framework.hardware import detect, optimize_gpu_memory
        prof = detect()
        return optimize_gpu_memory(prof)

    @app.get("/unified/stats")
    def unified_stats() -> dict[str, Any]:
        from harness_sidecar.framework.unified_memory import UnifiedPool
        from harness_sidecar.framework.hardware import detect
        if not hasattr(app.state, "pool"):
            prof = detect()
            app.state.pool = UnifiedPool(gpu_backend=prof.backend)
        return app.state.pool.stats()

    @app.post("/unified/alloc")
    def unified_alloc(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.unified_memory import UnifiedPool
        from harness_sidecar.framework.hardware import detect
        if not hasattr(app.state, "pool"):
            prof = detect()
            app.state.pool = UnifiedPool(gpu_backend=prof.backend)
        name = body.get("name", "buf")
        size = int(body.get("size", 1024))
        prefer = bool(body.get("prefer_gpu", False))
        buf = app.state.pool.alloc(name, size, prefer)
        return {"name": buf.name, "size": buf.size, "backend": buf.backend}


    @app.get("/metrics")
    def metrics() -> dict[str, Any]:
        from harness_sidecar.framework.metrics import collect, to_dict
        from harness_sidecar.framework.hardware import detect
        prof = detect()
        return to_dict(collect(prof.backend))

    @app.post("/hardware/vram")
    def vram_optimize() -> dict[str, Any]:
        from harness_sidecar.framework.unified_memory import UnifiedPool, optimize_vram
        from harness_sidecar.framework.hardware import detect
        if not hasattr(app.state, "pool"):
            prof = detect()
            app.state.pool = UnifiedPool(gpu_backend=prof.backend)
        return optimize_vram(app.state.pool)


    @app.get("/backends")
    def backends() -> dict[str, Any]:
        from harness_sidecar.framework.backends import get_backend
        out = {}
        for name in ("cuda", "hip", "cpu"):
            b = get_backend(name)
            out[name] = {"available": b.available(), "info": b.info()}
        return out

    @app.get("/diagram/{name}")
    def diagram(name: str) -> dict[str, Any]:
        from harness_sidecar.framework.ml.designer.graph import ModelGraph, Node
        from harness_sidecar.framework.ml.designer.diagram import to_mermaid, to_ascii, to_svg_stub
        # Demo graph if no saved graph; in production load from builder
        g = ModelGraph(name)
        g.add_node(Node("in", "input", {}, 0, 0))
        g.add_node(Node("attn", "attention", {}, 100, 0))
        g.add_node(Node("ff", "ff", {}, 200, 0))
        g.add_node(Node("out", "output", {}, 300, 0))
        g.add_edge("in", "attn")
        g.add_edge("attn", "ff")
        g.add_edge("ff", "out")
        return {"mermaid": to_mermaid(g), "ascii": to_ascii(g), "svg": to_svg_stub(g)}


    @app.get("/frameworks")
    def frameworks() -> dict[str, Any]:
        from harness_sidecar.framework.backends.frameworks import list_frameworks
        return list_frameworks()

    @app.post("/frameworks/{name}/train")
    def framework_train(name: str, body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.backends.frameworks import get_framework
        try:
            b = get_framework(name)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        return b.train(body.get("spec", {}), body.get("data"), int(body.get("epochs", 1)))

    @app.post("/frameworks/{name}/infer")
    def framework_infer(name: str, body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.backends.frameworks import get_framework
        try:
            b = get_framework(name)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        return b.infer(None, body.get("inputs", [[0, 0, 0, 0]]))


    @app.post("/train/stop")
    def train_stop() -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        return app.state.pipeline.stop_all()


    @app.post("/train/stop/current")
    def train_stop_current() -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        return app.state.pipeline.stop_current()


    @app.post("/cancel/demo")
    def cancel_demo(body: dict[str, Any]) -> dict[str, Any]:
        """Demo the three cancellation techniques."""
        import asyncio
        from harness_sidecar.framework.ml.pipeline.cancel import (
            CancelToken, run_cooperative, run_async_cancel, run_with_timeout
        )
        kind = body.get("kind", "cooperative")
        if kind == "cooperative":
            token = CancelToken()
            # Cancel after a short delay in another thread
            import threading, time
            def _c():
                time.sleep(0.02)
                token.cancel()
            threading.Thread(target=_c, daemon=True).start()
            return run_cooperative(10, token)
        if kind == "async":
            return asyncio.run(run_async_cancel(10, 0.03))
        if kind == "timeout":
            return asyncio.run(run_with_timeout(10, 0.03))
        return {"error": "unknown kind"}


    @app.post("/train/main")
    def train_main(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            from harness_sidecar.framework.ml.pipeline.trainer import TrainingPipeline
            app.state.pipeline = TrainingPipeline()
        return app.state.pipeline.main_loop(int(body.get("steps", 5)))


    @app.get("/sandbox")
    def sandbox_status() -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        return app.state.sandbox.status()

    @app.post("/sandbox/toggle")
    def sandbox_toggle(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        app.state.sandbox.set_isolate(bool(body.get("isolate", True)))
        return app.state.sandbox.status()

    @app.post("/sandbox/run")
    def sandbox_run(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        cmd = body.get("cmd", ["echo", "hello"])
        if isinstance(cmd, str):
            cmd = cmd.split()
        return app.state.sandbox.run(cmd)

    @app.get("/sandbox/backends")
    def sandbox_backends() -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        return app.state.sandbox.available_backends()


    @app.post("/sandbox/network")
    def sandbox_network(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        app.state.sandbox.set_network(bool(body.get("enabled", False)))
        return app.state.sandbox.status()

    @app.post("/sandbox/gpu")
    def sandbox_gpu(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        app.state.sandbox.set_gpu(bool(body.get("enabled", False)))
        return app.state.sandbox.status()

    @app.post("/terminal")
    def terminal_run(body: dict[str, Any]) -> dict[str, Any]:
        """Run a command. Uses sandbox if isolate is on."""
        if not hasattr(app.state, "sandbox"):
            from harness_sidecar.framework.sandbox.manager import SandboxManager
            app.state.sandbox = SandboxManager()
        cmd = body.get("cmd", "echo hello")
        if isinstance(cmd, str):
            cmd = cmd.split()
        return app.state.sandbox.run(cmd)


    @app.post("/terminal/cmd")
    def terminal_cmd(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.cli.commands import dispatch
        if not hasattr(app.state, "activity"):
            from harness_sidecar.framework.cli.activity import ActivityLog
            app.state.activity = ActivityLog()
        line = body.get("line", "")
        app.state.activity.cmd(line)
        result = dispatch(line)
        if not result.get("ok"):
            app.state.activity.error(result.get("output", "error"))
        else:
            app.state.activity.debug(result.get("output", "")[:100])
        return result

    @app.get("/commands")
    def commands_list() -> dict[str, Any]:
        from harness_sidecar.framework.cli.commands import list_commands
        return {"commands": list_commands()}

    @app.get("/activity")
    def activity_get() -> dict[str, Any]:
        if not hasattr(app.state, "activity"):
            from harness_sidecar.framework.cli.activity import ActivityLog
            app.state.activity = ActivityLog()
        return {"entries": app.state.activity.recent(100)}

    @app.get("/activity/export")
    def activity_export() -> dict[str, Any]:
        if not hasattr(app.state, "activity"):
            from harness_sidecar.framework.cli.activity import ActivityLog
            app.state.activity = ActivityLog()
        return {"text": app.state.activity.export()}

    @app.post("/activity/clear")
    def activity_clear() -> dict[str, Any]:
        if not hasattr(app.state, "activity"):
            from harness_sidecar.framework.cli.activity import ActivityLog
            app.state.activity = ActivityLog()
        app.state.activity.clear()
        return {"ok": True}


    @app.get("/distill")
    def distill_list() -> dict[str, Any]:
        from harness_sidecar.framework.ml.distill import list_techniques
        return {"techniques": list_techniques()}

    @app.post("/distill")
    def distill_run(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.distill import response_distill, feature_distill, relation_distill
        kind = body.get("technique", "response")
        if kind == "response":
            return response_distill(body.get("teacher", [[1, 0]]), body.get("student", [[0.5, 0.5]]), body.get("temperature", 2.0), body.get("alpha", 0.7))
        if kind == "feature":
            return feature_distill(body.get("teacher", [[1, 0]]), body.get("student", [[0.8, 0.2]]))
        if kind == "relation":
            return relation_distill(body.get("teacher", [[1, 0], [0, 1]]), body.get("student", [[0.9, 0.1], [0.1, 0.9]]))
        return {"ok": False, "error": "unknown technique"}


    def _rama_stack():
        if not hasattr(app.state, "rama_states"):
            from harness_sidecar.framework.ml.rama.router import RAMA
            from harness_sidecar.framework.ml.rama.states import RAMAStates
            from harness_sidecar.framework.ml.rama.train.collector import TrainingCollector
            from harness_sidecar.framework.ml.rama.train.trainer import RAMATrainer
            def factory():
                return RAMA(lambda p, m: f"[{m}] {p[:40]}")
            app.state.rama_states = RAMAStates(factory)
            app.state.collector = TrainingCollector()
            app.state.rama_trainer = RAMATrainer(app.state.rama_states, app.state.collector)
        return app.state.rama_states, app.state.collector, app.state.rama_trainer

    @app.get("/rama/states")
    def rama_states() -> dict[str, Any]:
        s, _, _ = _rama_stack()
        return s.status()

    @app.post("/rama/states/backup")
    def rama_backup() -> dict[str, Any]:
        s, _, _ = _rama_stack()
        return {"id": s.snapshot_backup("manual")}

    @app.post("/rama/states/failover")
    def rama_failover() -> dict[str, Any]:
        s, _, _ = _rama_stack()
        return s.failover()

    @app.post("/rama/states/promote")
    def rama_promote() -> dict[str, Any]:
        s, _, _ = _rama_stack()
        return s.promote_training()

    @app.post("/rama/train/manual")
    def rama_train_manual(body: dict[str, Any]) -> dict[str, Any]:
        _, _, t = _rama_stack()
        return t.train_manual(body.get("prompt", ""), body.get("specialist", "general"))

    @app.post("/rama/train/auto")
    def rama_train_auto(body: dict[str, Any]) -> dict[str, Any]:
        _, _, t = _rama_stack()
        return t.train_auto(int(body.get("limit", 20)))

    @app.post("/rama/train/from-local")
    def rama_from_local(body: dict[str, Any]) -> dict[str, Any]:
        _, _, t = _rama_stack()
        return t.from_local(body.get("specialist", "general"), body.get("prompt", ""), lambda p, m: f"[{m}] {p}")

    @app.post("/rama/train/from-api")
    def rama_from_api(body: dict[str, Any]) -> dict[str, Any]:
        _, _, t = _rama_stack()
        return t.from_api(body.get("model", "api"), body.get("prompt", ""), body.get("response", ""))

    @app.get("/rama/train/data")
    def rama_train_data() -> dict[str, Any]:
        _, c, _ = _rama_stack()
        return {"records": c.list(), "count": len(c.records)}

    @app.post("/rama/train/export")
    def rama_train_export() -> dict[str, Any]:
        _, c, _ = _rama_stack()
        return {"path": c.export()}

    @app.get("/meta")
    def meta_list() -> dict[str, Any]:
        from harness_sidecar.framework.ml.meta.models import list_meta
        return {"models": list_meta()}

    @app.post("/meta/{name}")
    def meta_run(name: str, body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.ml.meta.models import get_meta
        m = get_meta(name)
        if not m:
            return {"ok": False, "error": "unknown meta-model"}
        return m.run(body.get("prompt", ""))


    @app.get("/catalog")
    def catalog(type: str | None = None) -> dict[str, Any]:
        from harness_sidecar.framework.models.catalog import catalog_for, types
        from harness_sidecar.framework.hardware import detect
        prof = detect()
        ram = prof.ram_gb or 8
        vram = sum(g.memory_mb for g in prof.gpus) / 1024 if prof.gpus else 0
        has_gpu = bool(prof.gpus)
        return {
            "types": types(),
            "hardware": {"ram_gb": ram, "vram_gb": round(vram, 1), "gpu": has_gpu, "backend": prof.backend},
            "models": catalog_for(ram, vram, has_gpu, type),
        }


    @app.post("/hf/download")
    def hf_download(body: dict[str, Any]) -> dict[str, Any]:
        from harness_sidecar.framework.models.hf import download
        return download(body.get("repo", ""), body.get("filename"), body.get("revision", "main"))

    @app.get("/hf/cached")
    def hf_cached() -> dict[str, Any]:
        from harness_sidecar.framework.models.hf import list_cached
        return {"cached": list_cached()}

    @app.get("/watchdog")
    def watchdog_status() -> dict[str, Any]:
        if not hasattr(app.state, "watchdog"):
            from harness_sidecar.framework.security.watchdog import Watchdog
            app.state.watchdog = Watchdog()
        return app.state.watchdog.status()

    @app.post("/watchdog/scan")
    def watchdog_scan(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "watchdog"):
            from harness_sidecar.framework.security.watchdog import Watchdog
            app.state.watchdog = Watchdog()
        return app.state.watchdog.scan_text(body.get("text", ""), body.get("source", "api"))

    @app.post("/watchdog/cleanup")
    def watchdog_cleanup(body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "watchdog"):
            from harness_sidecar.framework.security.watchdog import Watchdog
            app.state.watchdog = Watchdog()
        return app.state.watchdog.cleanup(body.get("source", ""))

    @app.get("/security")
    def security_list() -> dict[str, Any]:
        from harness_sidecar.framework.security.models import list_security
        return {"models": list_security()}

    @app.post("/security/{name}")
    def security_run(name: str, body: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(app.state, "watchdog"):
            from harness_sidecar.framework.security.watchdog import Watchdog
            app.state.watchdog = Watchdog()
        from harness_sidecar.framework.security.models import SecurityModel, SECURITY_MODELS
        desc = dict(SECURITY_MODELS).get(name, "")
        if not desc:
            return {"ok": False, "error": "unknown security model"}
        return SecurityModel(name, desc, app.state.watchdog).run(body.get("text", ""))


    @app.get("/watchdog/stream")
    def watchdog_stream():
        """SSE stream of Watchdog status."""
        import json
        from fastapi.responses import StreamingResponse
        def gen():
            if not hasattr(app.state, "watchdog"):
                from harness_sidecar.framework.security.watchdog import Watchdog
                app.state.watchdog = Watchdog()
            import time
            for _ in range(60):
                s = app.state.watchdog.status()
                yield f"data: {json.dumps(s)}\n\n"
                time.sleep(1)
        return StreamingResponse(gen(), media_type="text/event-stream")

    def _wd_trainer():
        if not hasattr(app.state, "watchdog"):
            from harness_sidecar.framework.security.watchdog import Watchdog
            app.state.watchdog = Watchdog()
        if not hasattr(app.state, "wd_trainer"):
            from harness_sidecar.framework.security.trainer import WatchdogTrainer
            app.state.wd_trainer = WatchdogTrainer(app.state.watchdog)
        return app.state.wd_trainer

    @app.get("/watchdog/train")
    def wd_train_status() -> dict[str, Any]:
        return _wd_trainer().status()

    @app.post("/watchdog/train/manual")
    def wd_train_manual(body: dict[str, Any]) -> dict[str, Any]:
        return _wd_trainer().train_manual(body.get("text", ""), body.get("kind", "manual"))

    @app.post("/watchdog/train/from-rama")
    def wd_train_rama() -> dict[str, Any]:
        if not hasattr(app.state, "rama"):
            return {"ok": False, "error": "no RAMA"}
        return _wd_trainer().train_from_rama(app.state.rama)

    @app.post("/watchdog/train/rollback")
    def wd_rollback() -> dict[str, Any]:
        return _wd_trainer().rollback()


    @app.get("/monitor/stream")
    def monitor_stream():
        """Unified SSE: watchdog + training jobs + metrics."""
        import json, time
        from fastapi.responses import StreamingResponse
        def gen():
            from harness_sidecar.framework.monitor import Monitor
            mon = Monitor()
            for _ in range(60):
                yield f"data: {json.dumps(mon.snapshot(app.state))}\n\n"
                time.sleep(1)
        return StreamingResponse(gen(), media_type="text/event-stream")

    @app.get("/monitor")
    def monitor_snapshot() -> dict[str, Any]:
        from harness_sidecar.framework.monitor import Monitor
        return Monitor().snapshot(app.state)

    @app.get("/monitor/logs")
    def monitor_logs() -> dict[str, Any]:
        if not hasattr(app.state, "activity"):
            from harness_sidecar.framework.cli.activity import ActivityLog
            app.state.activity = ActivityLog()
        return {"logs": app.state.activity.recent(50)}

    @app.get("/monitor/training")
    def monitor_training() -> dict[str, Any]:
        if not hasattr(app.state, "pipeline"):
            return {"jobs": [], "active": []}
        return {"jobs": app.state.pipeline.list_jobs(), "active": app.state.pipeline.active()}

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        @app.get("/")
        def index():
            return FileResponse(STATIC_DIR / "index.html")

    # Serve built React Web GUI if available
    REACT_DIST = Path(__file__).resolve().parents[3] / "dist"
    if REACT_DIST.exists() and (REACT_DIST / "index.html").exists():
        app.mount("/web", StaticFiles(directory=str(REACT_DIST), html=True), name="web")

        @app.get("/web-status")
        def web_status():
            return {"available": True, "url": "/web/"}
    else:
        @app.get("/web-status")
        def web_status():
            return {"available": False}

else:
    app = None
