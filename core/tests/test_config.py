# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

from pathlib import Path

from talos_craftia_core.config import load_config


def test_load_defaults(tmp_path: Path) -> None:
    cfg = load_config(user_path=tmp_path / "missing.toml", apply_env=False)
    assert cfg.config_version == 1
    assert cfg.hardware.preset == "auto"
    assert cfg.quality.mode == "standard"
    assert "planner" in cfg.roles


def test_gpu_6gb_user_file(tmp_path: Path) -> None:
    user = tmp_path / "craftia.toml"
    user.write_text(
        'config_version = 1\n[hardware]\npreset = "gpu_6gb"\n',
        encoding="ascii",
    )
    cfg = load_config(user_path=user, apply_env=False)
    assert cfg.hardware.preset == "gpu_6gb"
    assert "local_small" in cfg.providers
    assert cfg.roles["detailer"]["chain"][0] == "local_small"
