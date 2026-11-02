"""Convenience runner that uses the existing inference client."""

from harness_sidecar.inference.client import generate
from .core.agent import Agent
from .tools.defaults import make_default_registry


def run_agent(message: str, sources: list[str] | None = None, model: str = "phi4-mini", active_skills: list[str] | None = None) -> dict:
    agent = Agent(
        generate=generate,
        model=model,
        tools=make_default_registry(),
        active_skills=active_skills or [],
    )
    return agent.run(message, sources)
