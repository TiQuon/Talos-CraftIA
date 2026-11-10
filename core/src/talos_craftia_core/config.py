# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Layered configuration for hardware presets and LLM roles."""

from __future__ import annotations

import copy
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from talos_craftia_core.identity import repo_root

SUPPORTED_CONFIG_VERSION = 1
QUALITY_MODES = frozenset({"draft", "standard", "masterpiece"})
HARDWARE_PRESETS = frozenset(
    {
        "auto",
        "cpu_only",
        "gpu_6gb",
        "gpu_12gb",
        "gpu_24gb_plus",
        "cloud_only",
        "local_only",
        "custom",
    }
)


@dataclass
class QualityConfig:
    mode: str = "standard"
    max_wall_time_min: int = 90
    max_cost_usd: float = 5.0


@dataclass
class HardwareConfig:
    preset: str = "auto"


@dataclass
class AppConfig:
    config_version: int = SUPPORTED_CONFIG_VERSION
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    providers: dict[str, dict[str, Any]] = field(default_factory=dict)
    roles: dict[str, dict[str, Any]] = field(default_factory=dict)
    source_files: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.config_version != SUPPORTED_CONFIG_VERSION:
            raise ValueError(
                f"unsupported config_version {self.config_version}; "
                f"expected {SUPPORTED_CONFIG_VERSION}"
            )
        if self.hardware.preset not in HARDWARE_PRESETS:
            raise ValueError(f"unknown hardware preset: {self.hardware.preset}")
        if self.quality.mode not in QUALITY_MODES:
            raise ValueError(f"unknown quality mode: {self.quality.mode}")
        if self.quality.max_wall_time_min <= 0:
            raise ValueError("max_wall_time_min must be positive")
        if self.quality.max_cost_usd < 0:
            raise ValueError("max_cost_usd must be >= 0")
        for name, provider in self.providers.items():
            if "adapter" not in provider:
                raise ValueError(f"provider {name!r} missing adapter")
            if "api_key_env" in provider:
                env_name = provider["api_key_env"]
                if not isinstance(env_name, str) or not env_name:
                    raise ValueError(f"provider {name!r} api_key_env must be a name")
                # Never require the key to be present at validate time.
        for role, body in self.roles.items():
            chain = body.get("chain")
            if not isinstance(chain, list) or not chain:
                raise ValueError(f"role {role!r} needs a non-empty chain")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _defaults() -> dict[str, Any]:
    return {
        "config_version": SUPPORTED_CONFIG_VERSION,
        "hardware": {"preset": "auto"},
        "quality": {
            "mode": "standard",
            "max_wall_time_min": 90,
            "max_cost_usd": 5.0,
        },
        "providers": {},
        "roles": {
            "planner": {"chain": ["local_small"]},
            "detailer": {"chain": ["local_small"]},
        },
    }


def _apply_env(data: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(data)
    preset = os.environ.get("CRAFTIA_HARDWARE_PRESET")
    if preset:
        result.setdefault("hardware", {})["preset"] = preset
    mode = os.environ.get("CRAFTIA_QUALITY_MODE")
    if mode:
        result.setdefault("quality", {})["mode"] = mode
    return result


def _to_config(data: dict[str, Any], sources: list[str]) -> AppConfig:
    hardware = data.get("hardware", {})
    quality = data.get("quality", {})
    cfg = AppConfig(
        config_version=int(data.get("config_version", SUPPORTED_CONFIG_VERSION)),
        hardware=HardwareConfig(preset=str(hardware.get("preset", "auto"))),
        quality=QualityConfig(
            mode=str(quality.get("mode", "standard")),
            max_wall_time_min=int(quality.get("max_wall_time_min", 90)),
            max_cost_usd=float(quality.get("max_cost_usd", 5.0)),
        ),
        providers=dict(data.get("providers", {})),
        roles=dict(data.get("roles", {})),
        source_files=sources,
    )
    cfg.validate()
    return cfg


def load_config(
    user_path: Path | None = None,
    *,
    apply_env: bool = True,
) -> AppConfig:
    """Load config layers: defaults -> preset file -> user file -> env."""
    root = repo_root()
    sources: list[str] = ["defaults"]
    data = _defaults()

    # Resolve preset after reading a first-pass user hint if present.
    hint_preset = data["hardware"]["preset"]
    candidate_user = user_path
    if candidate_user is None:
        for name in ("craftia.toml", "talos_craftia.toml"):
            path = root / name
            if path.is_file():
                candidate_user = path
                break

    if candidate_user and candidate_user.is_file():
        user_data = _load_toml(candidate_user)
        hint_preset = (
            user_data.get("hardware", {}).get("preset", hint_preset) or hint_preset
        )

    if hint_preset and hint_preset not in {"auto", "custom"}:
        preset_path = root / "presets" / "hardware" / f"{hint_preset}.toml"
        if preset_path.is_file():
            data = _deep_merge(data, _load_toml(preset_path))
            sources.append(str(preset_path))

    if candidate_user and candidate_user.is_file():
        data = _deep_merge(data, _load_toml(candidate_user))
        sources.append(str(candidate_user))

    if apply_env:
        data = _apply_env(data)
        sources.append("env:CRAFTIA_*")

    return _to_config(data, sources)


def list_hardware_presets() -> list[str]:
    preset_dir = repo_root() / "presets" / "hardware"
    if not preset_dir.is_dir():
        return []
    return sorted(path.stem for path in preset_dir.glob("*.toml"))
