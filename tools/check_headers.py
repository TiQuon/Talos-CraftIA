#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Verify SPDX headers and ASCII-only executable sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CODE_SUFFIXES = {
    ".py",
    ".rs",
    ".java",
    ".ts",
    ".tsx",
    ".js",
    ".ps1",
    ".sh",
    ".toml",
    ".gradle",
    ".md",
    ".cff",
}
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "target",
    "node_modules",
    "workspace",
    "plans",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "LICENSES",
    "dist",
    "build",
}
SKIP_FILES = {"LICENSE", ".gitignore"}


def is_skipped(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    if path.name in SKIP_FILES:
        return True
    if path.suffix == "" and path.name.startswith("."):
        return True
    return False


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: not valid UTF-8"]
    if path.suffix in {".py", ".rs", ".java", ".ts", ".tsx", ".js", ".ps1", ".sh"}:
        try:
            text.encode("ascii")
        except UnicodeEncodeError:
            errors.append(f"{path}: non-ASCII in executable source")
    # Split marker strings so reuse lint does not parse this file as SPDX source.
    copy_mark = "SPDX-FileCopyrightText" + ":"
    lic_mark = "SPDX-License-Identifier" + ":"
    if copy_mark not in text and path.suffix in CODE_SUFFIXES:
        # gitkeep and pure binary annotations handled by REUSE.toml
        if path.name.endswith(".gitkeep"):
            return errors
        errors.append(f"{path}: missing SPDX-FileCopyrightText")
    if lic_mark not in text and path.suffix in CODE_SUFFIXES:
        if path.name.endswith(".gitkeep"):
            return errors
        errors.append(f"{path}: missing SPDX-License-Identifier")
    if "TiQuon_" not in text and path.suffix in {".py", ".rs", ".java", ".ts", ".tsx"}:
        errors.append(f"{path}: missing author marker TiQuon_")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue
        if path.suffix not in CODE_SUFFIXES and path.name not in {
            "README.md",
            "NOTICE",
            "AUTHORS",
            "CONTRIBUTING.md",
            "COMMERCIAL.md",
            "AUTHORIZED.md",
            "CLA.md",
        }:
            continue
        errors.extend(check_file(path))
    if errors:
        print("check_headers FAILED:")
        for err in errors:
            print(f"  {err}")
        return 1
    print("check_headers OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
