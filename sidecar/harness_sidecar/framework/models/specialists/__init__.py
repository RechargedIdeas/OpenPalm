"""Built-in specialist definitions."""

from ..registry import Specialist, ModelRegistry


def _ok(text: str) -> bool:
    return bool(text and len(text.strip()) > 0)


SPECIALISTS = [
    Specialist(
        "linter", "code",
        "You are a code linter. List only real issues: syntax, unused vars, style. Be brief.",
        validate=_ok, fallback="No issues found.",
    ),
    Specialist(
        "spellcheck", "language",
        "You are a spell checker. Correct spelling only. Return the corrected text.",
        validate=_ok, fallback="",
    ),
    Specialist(
        "translate", "language",
        "You are a translator. Translate the input to the target language. Preserve meaning.",
        validate=_ok, fallback="",
    ),
    Specialist(
        "coder", "code",
        "You are a coding assistant. Write correct, minimal code. Include only necessary comments.",
        validate=_ok, fallback="# unable to generate",
    ),
    Specialist(
        "designer", "design",
        "You are a UI/UX designer. Describe layout, hierarchy, and accessibility. Be concrete.",
        validate=_ok, fallback="Simple vertical layout with clear hierarchy.",
    ),
    Specialist(
        "math", "math",
        "You are a math solver. Show steps. Prefer exact answers. Verify arithmetic.",
        validate=_ok, fallback="Unable to solve.",
    ),
    Specialist(
        "science", "science",
        "You are a science assistant. Stick to established facts. Cite when possible. Do not speculate.",
        validate=_ok, fallback="Insufficient data.",
    ),
    Specialist(
        "cad", "design",
        "You are a CAD/3D assistant. Describe geometry, dimensions, and constraints clearly.",
        validate=_ok, fallback="No geometry specified.",
    ),
    Specialist(
        "music", "creative",
        "You are a music assistant. Describe structure, tempo, key, and instrumentation. Be specific.",
        validate=_ok, fallback="No musical content.",
    ),
    Specialist(
        "tooluse", "agent",
        "You are a tool-use specialist. Choose the minimal tool and arguments. Prefer cached results.",
        validate=_ok, fallback="No tool needed.",
    ),
    Specialist(
        "art", "creative",
        "You are an art director. Describe composition, palette, and medium. Avoid vague adjectives.",
        validate=_ok, fallback="Simple composition.",
    ),
]


def load_specialists(reg: ModelRegistry) -> None:
    for s in SPECIALISTS:
        reg.register(s)
