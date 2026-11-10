# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Command-line entry points for Talos CraftIA foundations."""

from __future__ import annotations

import argparse
import json
import sys

from talos_craftia_core import __author__, __version__
from talos_craftia_core.config import list_hardware_presets, load_config
from talos_craftia_core.doctor import run_doctor
from talos_craftia_core.identity import load_identity


def _cmd_about(_: argparse.Namespace) -> int:
    identity = load_identity()
    print(f"{identity.project_name} {__version__}")
    print(f"Author: {identity.author}")
    print(f"License (code): {identity.license_code}")
    print(f"License (data): {identity.license_data}")
    print(f"Project: {identity.project_url}")
    print("Source-available. Noncommercial use only unless separately licensed.")
    return 0


def _cmd_doctor(_: argparse.Namespace) -> int:
    report = run_doctor()
    print(json.dumps(report.to_dict(), indent=2))
    print(f"suggested_preset={report.suggested_preset}")
    return 0


def _cmd_config_show(_: argparse.Namespace) -> int:
    cfg = load_config()
    payload = {
        "config_version": cfg.config_version,
        "hardware": {"preset": cfg.hardware.preset},
        "quality": {
            "mode": cfg.quality.mode,
            "max_wall_time_min": cfg.quality.max_wall_time_min,
            "max_cost_usd": cfg.quality.max_cost_usd,
        },
        "providers": sorted(cfg.providers.keys()),
        "roles": {name: body.get("chain") for name, body in cfg.roles.items()},
        "sources": cfg.source_files,
        "available_presets": list_hardware_presets(),
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_identity(_: argparse.Namespace) -> int:
    identity = load_identity()
    print(
        json.dumps(
            {
                "project_name": identity.project_name,
                "slug": identity.slug,
                "mod_id": identity.mod_id,
                "mod_name": identity.mod_name,
                "author": identity.author,
                "project_url": identity.project_url,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="talos-craftia",
        description="Talos CraftIA foundations CLI (author TiQuon_).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"talos-craftia {__version__} by {__author__}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    about = sub.add_parser("about", help="Show project identity and license")
    about.set_defaults(func=_cmd_about)

    doctor = sub.add_parser("doctor", help="Detect hardware and suggest a preset")
    doctor.set_defaults(func=_cmd_doctor)

    config = sub.add_parser("config", help="Configuration helpers")
    config_sub = config.add_subparsers(dest="config_command", required=True)
    show = config_sub.add_parser("show", help="Show effective layered config")
    show.set_defaults(func=_cmd_config_show)

    identity = sub.add_parser("identity", help="Show identity.toml values")
    identity.set_defaults(func=_cmd_identity)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
