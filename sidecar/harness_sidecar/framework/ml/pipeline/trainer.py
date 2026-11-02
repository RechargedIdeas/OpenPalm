"""Self-training and manual training pipeline for RAMA and ML models.

Jobs run in background, persist across UI switches, and auto-recover.
"""

from __future__ import annotations

import hashlib
import re
import threading
from .cancel import CancelToken, Cancelled
import time
from dataclasses import dataclass, field
from typing import Any


def anonymize(text: str) -> str:
    """Strip emails, numbers that look like IDs, and long tokens."""
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[email]", text)
    text = re.sub(r"\b\d{6,}\b", "[id]", text)
    text = re.sub(r"\b[A-Za-z0-9]{20,}\b", "[token]", text)
    return text


@dataclass
class Job:
    id: str
    kind: str  # self, manual, ml
    target: str  # rama or model name
    status: str = "pending"  # pending, running, done, failed, recovered
    progress: float = 0.0
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    result: dict = field(default_factory=dict)
    error: str = ""
    cancel: threading.Event = field(default_factory=threading.Event)
    token: CancelToken = field(default_factory=CancelToken)



def _check_cancel(job: Job) -> bool:
    """Return True if the job should stop."""
    return job.token.cancelled() or job.cancel.is_set() or job.status == "stopped"

class TrainingPipeline:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self.telemetry_enabled = False
        self.telemetry: list[dict] = []
        self._lock = threading.Lock()
        self._threads: dict[str, threading.Thread] = {}

    def set_telemetry(self, enabled: bool) -> None:
        self.telemetry_enabled = enabled

    def collect(self, prompt: str, output: str, rating: int | None = None) -> None:
        if not self.telemetry_enabled:
            return
        self.telemetry.append({
            "prompt": anonymize(prompt),
            "output": anonymize(output),
            "rating": rating,
            "ts": time.time(),
        })
        # Cap
        if len(self.telemetry) > 500:
            self.telemetry.pop(0)

    def start_self_train(self, rama, min_samples: int = 3) -> str:
        """Auto-train RAMA from collected telemetry."""
        jid = f"self-{int(time.time()*1000)}"
        job = Job(id=jid, kind="self", target="rama")
        with self._lock:
            self.jobs[jid] = job
        t = threading.Thread(target=self._run_self, args=(jid, rama, min_samples), daemon=True)
        self._threads[jid] = t
        t.start()
        return jid

    def start_manual(self, rama, prompt: str, specialist: str) -> str:
        jid = f"manual-{int(time.time()*1000)}"
        job = Job(id=jid, kind="manual", target="rama")
        with self._lock:
            self.jobs[jid] = job
        t = threading.Thread(target=self._run_manual, args=(jid, rama, prompt, specialist), daemon=True)
        self._threads[jid] = t
        t.start()
        return jid

    def start_ml(self, builder, name: str, epochs: int) -> str:
        jid = f"ml-{int(time.time()*1000)}"
        job = Job(id=jid, kind="ml", target=name)
        with self._lock:
            self.jobs[jid] = job
        t = threading.Thread(target=self._run_ml, args=(jid, builder, name, epochs), daemon=True)
        self._threads[jid] = t
        t.start()
        return jid

    def _run_self(self, jid: str, rama, min_samples: int) -> None:
        job = self.jobs[jid]
        job.status = "running"
        try:
            samples = [t for t in self.telemetry if t.get("rating") and t["rating"] <= 2]
            if len(samples) < min_samples:
                job.status = "done"
                job.result = {"trained": 0, "reason": "not enough low-rated samples"}
                job.progress = 1.0
                return
            for i, s in enumerate(samples[:10]):
                if _check_cancel(job):
                    job.status = "stopped"
                    return
                job.progress = (i + 1) / min(10, len(samples))
                job.updated = time.time()
                if s.get("rating", 5) <= 2:
                    rama.train_route(s["prompt"], "tooluse")
                time.sleep(0.05)
            rama._save_version("self-train")
            job.status = "done"
            job.result = {"trained": min(10, len(samples))}
            job.progress = 1.0
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            self._recover(jid, rama)

    def _run_manual(self, jid: str, rama, prompt: str, specialist: str) -> None:
        job = self.jobs[jid]
        job.status = "running"
        try:
            if _check_cancel(job):
                job.status = "stopped"
                return
            job.progress = 0.5
            rama.train_route(anonymize(prompt), specialist)
            rama._save_version(f"manual-{specialist}")
            job.progress = 1.0
            job.status = "done"
            job.result = {"specialist": specialist}
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            self._recover(jid, rama)

    def _run_ml(self, jid: str, builder, name: str, epochs: int) -> None:
        job = self.jobs[jid]
        job.status = "running"
        try:
            for i in range(epochs):
                if _check_cancel(job):
                    job.status = "stopped"
                    return
                job.progress = (i + 1) / epochs
                job.updated = time.time()
                builder.train(name, 1)
                time.sleep(0.05)
            job.status = "done"
            job.result = {"epochs": epochs}
            job.progress = 1.0
        except Exception as e:
            job.status = "failed"
            job.error = str(e)

    def _recover(self, jid: str, rama) -> None:
        """Rollback to last good version on failure."""
        job = self.jobs[jid]
        if rama.rollback():
            job.status = "recovered"
            job.result = {"recovered": True}




    def main_loop(self, steps: int = 10) -> dict:
        """Main training loop with cooperative cancellation."""
        jid = f"main-{int(time.time()*1000)}"
        job = Job(id=jid, kind="main", target="pipeline")
        with self._lock:
            self.jobs[jid] = job
        job.status = "running"
        done = 0
        try:
            for i in range(steps):
                if _check_cancel(job):
                    job.status = "stopped"
                    return {"id": jid, "status": "stopped", "done": done}
                job.progress = (i + 1) / steps
                job.updated = time.time()
                time.sleep(0.02)
                done += 1
            job.status = "done"
            job.progress = 1.0
            return {"id": jid, "status": "done", "done": done}
        except Cancelled:
            job.status = "stopped"
            return {"id": jid, "status": "cancelled", "done": done}

    def stop_current(self) -> dict:
        """Stop the most recent running or pending job."""
        with self._lock:
            candidates = [j for j in self.jobs.values() if j.status in ("pending", "running")]
            if not candidates:
                return {"stopped": None, "count": 0}
            # Most recently updated
            target = max(candidates, key=lambda j: j.updated)
            target.token.cancel()
            target.cancel.set()
            target.status = "stopped"
            target.updated = time.time()
            return {"stopped": target.id, "count": 1}

    def stop_all(self) -> dict:
        """Mark all running/pending jobs as stopped."""
        stopped = []
        with self._lock:
            for jid, job in self.jobs.items():
                if job.status in ("pending", "running"):
                    job.token.cancel()
                    job.cancel.set()
                    job.status = "stopped"
                    job.updated = time.time()
                    stopped.append(jid)
        return {"stopped": stopped, "count": len(stopped)}

    def status(self, jid: str) -> dict | None:
        job = self.jobs.get(jid)
        if not job:
            return None
        return {
            "id": job.id, "kind": job.kind, "target": job.target,
            "status": job.status, "progress": job.progress,
            "result": job.result, "error": job.error,
        }

    def list_jobs(self) -> list[dict]:
        return [self.status(j) for j in self.jobs]

    def active(self) -> list[dict]:
        return [j for j in self.list_jobs() if j and j["status"] in ("pending", "running")]
