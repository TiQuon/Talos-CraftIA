<!--
SPDX-FileCopyrightText: 2026 TiQuon_
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Development

## Toolchains

- Python 3.12 or 3.13 via `uv`
- Rust stable via `rustup` (Windows needs Visual Studio Build Tools with C++ / MSVC)
- Git

Optional tools: `reuse`, `ruff`, `cargo-deny` (after MSVC is available).

## Common commands

```bat
cd core
uv sync --extra dev
uv run talos-craftia doctor
uv run pytest
cd ..
powershell -File tools\check.ps1
```

Identity dry-run rename:

```bat
python tools\rename.py --new-slug example_slug --new-name "Example Name"
```

## Layout notes

- `engine/`, `mod/`, and `web/` are placeholders until later phases.
- Local caches go under `workspace/` (ignored by git).
- Copy `craftia.toml.example` to `craftia.toml` for personal config (ignored by git).
