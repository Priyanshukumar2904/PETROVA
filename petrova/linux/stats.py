"""
Hardware & System Telemetry Engine for PETROVA.
Extracts live CPU temperatures, RAM/Disk metrics, and exact Linux distribution identity.
"""

import os
import re
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def get_distro_info() -> Dict[str, str]:
    """Parse /etc/os-release and identify package managers."""
    info = {
        "name": "Linux",
        "pretty_name": "Linux",
        "id": "linux",
        "id_like": "",
        "package_manager": "unknown",
        "aur_helper": "none",
    }

    os_release = Path("/etc/os-release")
    if os_release.exists():
        try:
            with open(os_release, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        v = v.strip('"\'')
                        if k == "NAME":
                            info["name"] = v
                        elif k == "PRETTY_NAME":
                            info["pretty_name"] = v
                        elif k == "ID":
                            info["id"] = v.lower()
                        elif k == "ID_LIKE":
                            info["id_like"] = v.lower()
        except Exception:
            pass

    # Detect package manager
    if shutil.which("pacman"):
        info["package_manager"] = "pacman"
    elif shutil.which("apt"):
        info["package_manager"] = "apt"
    elif shutil.which("dnf"):
        info["package_manager"] = "dnf"
    elif shutil.which("zypper"):
        info["package_manager"] = "zypper"
    elif shutil.which("nix"):
        info["package_manager"] = "nix"

    # Detect AUR helper
    if shutil.which("paru"):
        info["aur_helper"] = "paru"
    elif shutil.which("yay"):
        info["aur_helper"] = "yay"

    return info


def get_cpu_temp() -> Optional[float]:
    """Retrieve highest core or package CPU temperature in Celsius."""
    # 1. Check thermal_zone sysfs
    temps = []
    thermal_dir = Path("/sys/class/thermal")
    if thermal_dir.exists():
        for zone in thermal_dir.glob("thermal_zone*/temp"):
            try:
                val = int(zone.read_text().strip())
                if val > 0:
                    celsius = val / 1000.0 if val > 1000 else float(val)
                    if 15.0 <= celsius <= 115.0:
                        temps.append(celsius)
            except Exception:
                continue

    # 2. Check hwmon devices
    hwmon_dir = Path("/sys/class/hwmon")
    if hwmon_dir.exists():
        for temp_file in hwmon_dir.glob("hwmon*/temp*_input"):
            try:
                val = int(temp_file.read_text().strip())
                if val > 0:
                    celsius = val / 1000.0 if val > 1000 else float(val)
                    if 15.0 <= celsius <= 115.0:
                        temps.append(celsius)
            except Exception:
                continue

    if temps:
        return round(max(temps), 1)
    return None


def get_ram_usage() -> Dict[str, Any]:
    """Calculate live RAM usage in GB and percentage from /proc/meminfo."""
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])

        total_kb = meminfo.get("MemTotal", 0)
        avail_kb = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
        used_kb = total_kb - avail_kb

        total_gb = round(total_kb / (1024 * 1024), 1)
        used_gb = round(used_kb / (1024 * 1024), 1)
        pct = round((used_kb / total_kb) * 100, 1) if total_kb > 0 else 0

        return {"total_gb": total_gb, "used_gb": used_gb, "pct": pct}
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "pct": 0}


def get_disk_usage(path: str = "/") -> Dict[str, Any]:
    """Retrieve root partition disk usage."""
    try:
        st = os.statvfs(path)
        total_gb = round((st.f_blocks * st.f_frsize) / (1024**3), 1)
        free_gb = round((st.f_bavail * st.f_frsize) / (1024**3), 1)
        used_gb = round(total_gb - free_gb, 1)
        pct = round((used_gb / total_gb) * 100, 1) if total_gb > 0 else 0
        return {"total_gb": total_gb, "used_gb": used_gb, "free_gb": free_gb, "pct": pct}
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "pct": 0}


def get_system_telemetry() -> Dict[str, Any]:
    """Collect complete live system metrics."""
    distro = get_distro_info()
    cpu_temp = get_cpu_temp()
    ram = get_ram_usage()
    disk = get_disk_usage()
    uname = platform.uname()

    return {
        "distro": distro,
        "cpu_temp": cpu_temp,
        "ram": ram,
        "disk": disk,
        "kernel": f"{uname.release} ({uname.machine})",
    }


def get_telemetry_bar() -> str:
    """Generate compact one-line telemetry status string for headers and response footers."""
    data = get_system_telemetry()
    temp_str = f"🌡️ {data['cpu_temp']}°C" if data["cpu_temp"] else "🌡️ N/A"
    ram_str = f"🧠 {data['ram']['used_gb']}/{data['ram']['total_gb']}GB ({data['ram']['pct']}%)"
    disk_str = f"💾 {data['disk']['used_gb']}/{data['disk']['total_gb']}GB ({data['disk']['pct']}%)"
    distro_str = f"🐧 {data['distro']['pretty_name']}"

    return f"[dim]{distro_str}  •  {temp_str}  •  {ram_str}  •  {disk_str}[/dim]"
