<!--
SPDX-FileCopyrightText: 2026 TiQuon_
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Talos CraftIA

Source-available toolkit to design detailed Minecraft environments with AI
(local models and/or external APIs). Built for quality over speed.

**Author:** TiQuon_  
**License (software):** [PolyForm Noncommercial 1.0.0](LICENSES/PolyForm-Noncommercial-1.0.0.txt)  
**License (data/docs):** [CC-BY-NC-4.0](LICENSES/CC-BY-NC-4.0.txt)  
**Commercial use:** requires a separate written license ([COMMERCIAL.md](COMMERCIAL.md))

Parts of this project may have been designed or written with AI assistance.
Parts are not itemized.

## Status

Pre-alpha foundations (`0.1.0`): identity, layered config, hardware doctor,
legal scaffolding. The voxel engine, Minecraft mod bridge, and LLM agents
come in later phases.

## Quick start

Requirements:

- Python 3.12 or 3.13 (managed via [uv](https://github.com/astral-sh/uv))
- Rust stable + MSVC Build Tools on Windows (needed from the engine phase)
- Git

```bat
cd core
uv sync --extra dev
uv run talos-craftia about
uv run talos-craftia doctor
uv run pytest
```

Copy `craftia.toml.example` to `craftia.toml` (gitignored) for local settings.
Never commit API keys; use environment variables named in `api_key_env`.

## Repository layout

| Path | Purpose |
|------|---------|
| `core/` | Python orchestrator foundations |
| `engine/` | Rust voxel engine (next phase) |
| `mod/` | NeoForge bridge mod (later) |
| `web/` | Local web UI (later) |
| `presets/` | Hardware and style presets |
| `profiles/` | Project profiles (e.g. VevanLand lore links) |
| `tools/` | Repo checks and rename helpers |
| `workspace/` | Local caches (gitignored) |

Private planning notes stay outside the published tree and are not pushed.

## Identity

Canonical names live in `identity.toml` (`mod_id = talos_craftia`). Renaming
is supported via `tools/rename.py` (dry-run by default).

## Security

Do not commit:

- API keys, `.env`, tokens, private emails
- Minecraft jars or textures
- Local `workspace/` catalogs and job traces
- Private planning documents

## Links

- GitHub: https://github.com/TiQuon/Talos-CraftIA
- NeoForge docs (for the future mod): https://docs.neoforged.net
