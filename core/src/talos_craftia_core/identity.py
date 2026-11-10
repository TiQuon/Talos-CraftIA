# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Load and validate project identity from identity.toml."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

MOD_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


@dataclass(frozen=True)
class Identity:
    project_name: str
    slug: str
    mod_id: str
    mod_name: str
    java_group: str
    python_pkg: str
    rust_prefix: str
    github_owner: str
    github_repo: str
    project_url: str
    author: str
    license_code: str
    license_data: str
    legacy_slugs: tuple[str, ...] = field(default_factory=tuple)
    legacy_mod_ids: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not MOD_ID_RE.match(self.mod_id):
            raise ValueError(
                f"mod_id {self.mod_id!r} must match [a-z][a-z0-9_]{{1,63}}"
            )
        if not MOD_ID_RE.match(self.slug):
            raise ValueError(f"slug {self.slug!r} must match [a-z][a-z0-9_]{{1,63}}")
        if self.author != "TiQuon_":
            raise ValueError("author must remain TiQuon_ unless identity is updated")


def repo_root() -> Path:
    """Return CraftIA repo root (parent of core/)."""
    return Path(__file__).resolve().parents[3]


def load_identity(path: Path | None = None) -> Identity:
    identity_path = path or (repo_root() / "identity.toml")
    with identity_path.open("rb") as handle:
        data = tomllib.load(handle)
    current = data["current"]
    legacy = data.get("legacy", {})
    identity = Identity(
        project_name=current["project_name"],
        slug=current["slug"],
        mod_id=current["mod_id"],
        mod_name=current["mod_name"],
        java_group=current["java_group"],
        python_pkg=current["python_pkg"],
        rust_prefix=current["rust_prefix"],
        github_owner=current["github_owner"],
        github_repo=current["github_repo"],
        project_url=current["project_url"],
        author=current["author"],
        license_code=current["license_code"],
        license_data=current["license_data"],
        legacy_slugs=tuple(legacy.get("slugs", [])),
        legacy_mod_ids=tuple(legacy.get("mod_ids", [])),
    )
    identity.validate()
    return identity
