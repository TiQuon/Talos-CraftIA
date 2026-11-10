#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Validate identity.toml against NeoForge mod_id rules."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "src"))

from talos_craftia_core.identity import load_identity  # noqa: E402


def main() -> int:
    identity = load_identity(ROOT / "identity.toml")
    print(f"identity OK: {identity.project_name} / {identity.mod_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
