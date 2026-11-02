"""OpenPalm CLI.

Usage:
  python -m harness_sidecar.cli chat "your message"
  python -m harness_sidecar.cli specialist math "2+2"
  python -m harness_sidecar.cli tools
  python -m harness_sidecar.cli snapshot list
"""

import argparse
import json
import sys

from harness_sidecar.framework.run import run_agent
from harness_sidecar.framework.models.router import ModelRouter
from harness_sidecar.inference.client import generate
from harness_sidecar.framework.tools.defaults import make_default_registry
from harness_sidecar.framework.resilience.snapshot import SnapshotStore


def cmd_chat(args):
    r = run_agent(args.message, sources=args.sources or [], active_skills=args.skills or [])
    print(r["draft"])
    if args.json:
        print(json.dumps(r["stats"]))


def cmd_specialist(args):
    router = ModelRouter(generate)
    r = router.run(args.name, args.prompt)
    print(r.get("output", r.get("error")))
    if args.json:
        print(json.dumps(r))


def cmd_tools(_args):
    reg = make_default_registry()
    for n in reg.list():
        print(n)


def cmd_snapshot(args):
    store = SnapshotStore()
    if args.action == "list":
        for s in store.list():
            print(s)
    elif args.action == "take":
        sid = store.take({"note": args.note or "cli"})
        print(sid)


def main():
    p = argparse.ArgumentParser(prog="openpalm")
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("chat")
    c.add_argument("message")
    c.add_argument("--sources", nargs="*")
    c.add_argument("--skills", nargs="*")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_chat)

    s = sub.add_parser("specialist")
    s.add_argument("name")
    s.add_argument("prompt")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_specialist)

    t = sub.add_parser("tools")
    t.set_defaults(func=cmd_tools)

    sn = sub.add_parser("snapshot")
    sn.add_argument("action", choices=["list", "take"])
    sn.add_argument("--note")
    sn.set_defaults(func=cmd_snapshot)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
