# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

from talos_craftia_core.identity import load_identity


def test_load_identity_defaults() -> None:
    identity = load_identity()
    assert identity.project_name == "Talos CraftIA"
    assert identity.mod_id == "talos_craftia"
    assert identity.author == "TiQuon_"
    assert identity.github_repo == "Talos-CraftIA"
