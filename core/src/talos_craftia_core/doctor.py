# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

"""Hardware and backend autodetection."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class GpuInfo:
    name: str | None = None
    vram_mib: int | None = None


@dataclass
class DoctorReport:
    os_name: str
    cpu_count: int
    ram_gib: float | None
    gpu: GpuInfo
    backends: dict[str, bool] = field(default_factory=dict)
    suggested_preset: str = "cpu_only"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "os": self.os_name,
            "cpu_count": self.cpu_count,
            "ram_gib": self.ram_gib,
            "gpu": {"name": self.gpu.name, "vram_mib": self.gpu.vram_mib},
            "backends": self.backends,
            "suggested_preset": self.suggested_preset,
            "notes": self.notes,
        }


def _probe_nvidia() -> GpuInfo:
    if shutil.which("nvidia-smi") is None:
        return GpuInfo()
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return GpuInfo()
    if completed.returncode != 0 or not completed.stdout.strip():
        return GpuInfo()
    line = completed.stdout.strip().splitlines()[0]
    parts = [part.strip() for part in line.split(",")]
    name = parts[0] if parts else None
    vram = None
    if len(parts) > 1:
        try:
            vram = int(float(parts[1]))
        except ValueError:
            vram = None
    return GpuInfo(name=name, vram_mib=vram)


def _probe_ram_gib() -> float | None:
    if platform.system() == "Windows":
        try:
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if completed.returncode == 0 and completed.stdout.strip():
                return round(int(completed.stdout.strip()) / (1024**3), 1)
        except (OSError, subprocess.SubprocessError, ValueError):
            return None
    try:
        page = os.sysconf("SC_PAGE_SIZE")
        phys = os.sysconf("SC_PHYS_PAGES")
        return round((page * phys) / (1024**3), 1)
    except (AttributeError, ValueError, OSError):
        return None


def _http_ok(url: str, timeout: float = 1.5) -> bool:
    try:
        req = Request(url, headers={"User-Agent": "TalosCraftIA-doctor/0.1"})
        with urlopen(req, timeout=timeout) as response:  # noqa: S310 - local probe only
            return 200 <= int(getattr(response, "status", 200)) < 500
    except (URLError, TimeoutError, OSError, ValueError):
        return False


def _probe_backends() -> dict[str, bool]:
    return {
        "ollama": shutil.which("ollama") is not None or _http_ok("http://127.0.0.1:11434/"),
        "openai_compatible_local": _http_ok("http://127.0.0.1:1234/v1/models")
        or _http_ok("http://127.0.0.1:8080/v1/models"),
        "anthropic_key_env": bool(
            os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CRAFTIA_API_KEY")
        ),
        "openai_key_env": bool(os.environ.get("OPENAI_API_KEY")),
        "gemini_key_env": bool(
            os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        ),
    }


def suggest_preset(gpu: GpuInfo, backends: dict[str, bool]) -> tuple[str, list[str]]:
    notes: list[str] = []
    vram = gpu.vram_mib or 0
    has_cloud = any(
        backends.get(key)
        for key in ("anthropic_key_env", "openai_key_env", "gemini_key_env")
    )
    has_local = backends.get("ollama") or backends.get("openai_compatible_local")

    if vram <= 0:
        notes.append("No NVIDIA GPU detected via nvidia-smi.")
        if has_cloud and not has_local:
            return "cloud_only", notes
        return "cpu_only", notes

    notes.append(f"Detected GPU: {gpu.name} ({vram} MiB).")
    if vram < 8000:
        preset = "gpu_6gb"
    elif vram < 20000:
        preset = "gpu_12gb"
    else:
        preset = "gpu_24gb_plus"

    if not has_local and has_cloud:
        notes.append("Cloud API keys found; local LLM server not detected.")
    if has_local:
        notes.append("Local OpenAI-compatible endpoint or Ollama detected.")
    return preset, notes


def run_doctor() -> DoctorReport:
    gpu = _probe_nvidia()
    backends = _probe_backends()
    preset, notes = suggest_preset(gpu, backends)
    return DoctorReport(
        os_name=f"{platform.system()} {platform.release()}",
        cpu_count=os.cpu_count() or 1,
        ram_gib=_probe_ram_gib(),
        gpu=gpu,
        backends=backends,
        suggested_preset=preset,
        notes=notes,
    )
