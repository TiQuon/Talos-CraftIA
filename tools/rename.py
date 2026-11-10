#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Dry-run rename helper for project identity tokens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "src"))

from talos_craftia_core.identity import MOD_ID_RE, load_identity  # noqa: E402

SKIP_DIRS = {
    ".git",
    ".venv",
    "target",
    "node_modules",
    "workspace",
    "plans",
    "LICENSES",
    "__pycache__",
}


def tokens_from(slug: str, project_name: str, java_group: str) -> dict[str, str]:
    return {
        "project_name": project_name,
        "slug": slug,
        "mod_id": slug,
        "java_group": java_group,
        "python_pkg": f"{slug}_core",
        "rust_prefix": f"{slug}-",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename Talos CraftIA identity tokens")
    parser.add_argument("--new-slug", required=True, help="New technical slug / mod_id")
    parser.add_argument("--new-name", required=True, help="New display name")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)",
    )
    args = parser.parse_args()
    if not MOD_ID_RE.match(args.new_slug):
        print("error: --new-slug must match [a-z][a-z0-9_]{1,63}")
        return 2

    current = load_identity(ROOT / "identity.toml")
    old = tokens_from(current.slug, current.project_name, current.java_group)
    new_group = f"dev.tiquon.{args.new_slug}"
    new = tokens_from(args.new_slug, args.new_name, new_group)

    replacements = [
        (old["project_name"], new["project_name"]),
        (old["java_group"], new["java_group"]),
        (old["python_pkg"], new["python_pkg"]),
        (old["rust_prefix"], new["rust_prefix"]),
        (old["slug"], new["slug"]),
    ]

    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in {".png", ".nbt", ".jar", ".exe"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated = text
        changed = False
        for src, dst in replacements:
            if src and src in updated:
                updated = updated.replace(src, dst)
                changed = True
        if changed:
            rel = path.relative_to(ROOT).as_posix()
            hits.append(rel)
            if args.apply:
                path.write_text(updated, encoding="utf-8", newline="\n")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: {len(hits)} files would change" if not args.apply else f"{mode}: {len(hits)} files changed")
    for rel in hits[:50]:
        print(f"  {rel}")
    if len(hits) > 50:
        print(f"  ... and {len(hits) - 50} more")
    if not args.apply:
        print("Re-run with --apply to write changes, then update identity.toml [current].")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
