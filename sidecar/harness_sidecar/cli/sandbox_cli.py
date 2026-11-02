"""CLI for sandbox and general commands.

Usage:
  python -m harness_sidecar.cli.sandbox_cli status
  python -m harness_sidecar.cli.sandbox_cli run echo hello
  python -m harness_sidecar.cli.sandbox_cli toggle isolate off
  python -m harness_sidecar.cli.sandbox_cli toggle network on
  python -m harness_sidecar.cli.sandbox_cli toggle gpu on
"""

import argparse
import sys

from harness_sidecar.framework.sandbox.manager import SandboxManager


def main():
    p = argparse.ArgumentParser(prog="openpalm-sandbox")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status")

    r = sub.add_parser("run")
    r.add_argument("command", nargs="+")

    t = sub.add_parser("toggle")
    t.add_argument("what", choices=["isolate", "network", "gpu"])
    t.add_argument("state", choices=["on", "off"])

    args = p.parse_args()
    m = SandboxManager()

    if args.cmd == "status":
        s = m.status()
        print(f"isolate={s['isolate']} network={s['policy']['network']} gpu={s['policy']['allow_gpu']} backend={s['backend']}")
    elif args.cmd == "run":
        result = m.run(args.command)
        print(result.get("stdout", ""))
        if result.get("stderr"):
            print(result["stderr"], file=sys.stderr)
        sys.exit(0 if result.get("ok") else 1)
    elif args.cmd == "toggle":
        on = args.state == "on"
        if args.what == "isolate":
            m.set_isolate(on)
        elif args.what == "network":
            m.set_network(on)
        elif args.what == "gpu":
            m.set_gpu(on)
        print(m.status()["policy"])
    else:
        p.print_help()


if __name__ == "__main__":
    main()
