"""20 meta-models specialized for designing and developing AI/ML systems.

Each is a thin specialist that returns structured advice or a stub artifact.
"""

from __future__ import annotations

META_MODELS = [
    ("architect", "Design overall model architecture and data flow"),
    ("dataset", "Plan datasets, splits, and labeling"),
    ("loss", "Choose and combine loss functions"),
    ("optimizer", "Select optimizer, schedule, and hyperparameters"),
    ("regularizer", "Recommend dropout, weight decay, augmentation"),
    ("evaluator", "Design metrics, eval sets, and ablations"),
    ("deployer", "Plan serving, batching, and quantization"),
    ("monitor", "Define drift detection and alerting"),
    ("debugger", "Diagnose training failures and NaNs"),
    ("compressor", "Suggest pruning, distillation, and quantization"),
    ("router", "Design MoE/MoA routing and gating"),
    ("tokenizer", "Advise on tokenization and vocabulary"),
    ("embedder", "Choose embedding dimensions and pooling"),
    ("attention", "Configure attention heads and masks"),
    ("scheduler", "Build learning-rate and warmup schedules"),
    ("augmenter", "Propose data augmentation pipelines"),
    ("aligner", "Plan RLHF / preference alignment"),
    ("safety", "Add refusal, filtering, and audit hooks"),
    ("benchmarker", "Select benchmarks and scoring"),
    ("orchestrator", "Coordinate multi-model pipelines"),
]


class MetaModel:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc

    def run(self, prompt: str) -> dict:
        return {
            "model": self.name,
            "desc": self.desc,
            "advice": f"[{self.name}] For '{prompt[:60]}': apply {self.desc.lower()}.",
            "steps": [
                f"1. Analyze the request in the {self.name} domain",
                f"2. {self.desc}",
                "3. Produce a reusable artifact or config",
            ],
        }


def get_meta(name: str) -> MetaModel | None:
    for n, d in META_MODELS:
        if n == name:
            return MetaModel(n, d)
    return None


def list_meta() -> list[dict]:
    return [{"name": n, "desc": d} for n, d in META_MODELS]
