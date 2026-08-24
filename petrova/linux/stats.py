"""
Hardware & System Telemetry Engine for PETROVA.
Extracts live CPU temperatures, RAM/Disk metrics, battery state, uptime, and exact Linux distribution identity.
"""

import os
import re
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


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
    temps = []
    # 1. Check thermal_zone sysfs
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


def get_battery_status() -> Dict[str, Any]:
    """
    Read live battery telemetry from /sys/class/power_supply.
    Detects state (Charging, Discharging, Full), percentage, plugged-in status, and estimated remaining time.
    """
    result = {
        "present": False,
        "percent": None,
        "status": "No Battery (Desktop/VM)",
        "plugged_in": False,
        "time_str": None,
        "icon": "🖥️",
    }

    psy = Path("/sys/class/power_supply")
    if not psy.exists():
        return result

    # 1. Check AC adapter status
    for ac in list(psy.glob("AC*")) + list(psy.glob("ADP*")) + list(psy.glob("ucsi*")):
        online_file = ac / "online"
        if online_file.exists():
            try:
                if int(online_file.read_text().strip()) == 1:
                    result["plugged_in"] = True
                    break
            except Exception:
                pass

    # 2. Check battery devices
    bats = list(psy.glob("BAT*")) + list(psy.glob("battery*"))
    if not bats:
        if result["plugged_in"]:
            result["status"] = "AC Connected (No Battery)"
        return result

    b = bats[0]
    result["present"] = True

    # Capacity
    cap_file = b / "capacity"
    if cap_file.exists():
        try:
            result["percent"] = int(cap_file.read_text().strip())
        except Exception:
            pass

    # Status
    status_file = b / "status"
    raw_status = status_file.read_text().strip() if status_file.exists() else "Unknown"
    result["status"] = raw_status

    # Estimate time remaining or charging time
    charge_now = int((b / "charge_now").read_text().strip()) if (b / "charge_now").exists() else None
    charge_full = int((b / "charge_full").read_text().strip()) if (b / "charge_full").exists() else None
    current_now = int((b / "current_now").read_text().strip()) if (b / "current_now").exists() else None

    energy_now = int((b / "energy_now").read_text().strip()) if (b / "energy_now").exists() else None
    energy_full = int((b / "energy_full").read_text().strip()) if (b / "energy_full").exists() else None
    power_now = int((b / "power_now").read_text().strip()) if (b / "power_now").exists() else None

    status_lower = raw_status.lower()
    if status_lower == "discharging":
        result["icon"] = "🔋"
        if charge_now and current_now and current_now > 0:
            hrs = charge_now / current_now
            h = int(hrs)
            m = int((hrs - h) * 60)
            result["time_str"] = f"~{h}h {m}m left"
        elif energy_now and power_now and power_now > 0:
            hrs = energy_now / power_now
            h = int(hrs)
            m = int((hrs - h) * 60)
            result["time_str"] = f"~{h}h {m}m left"
    elif status_lower == "charging":
        result["icon"] = "⚡"
        result["plugged_in"] = True
        if charge_full and charge_now and current_now and current_now > 0:
            hrs = max(0, (charge_full - charge_now)) / current_now
            h = int(hrs)
            m = int((hrs - h) * 60)
            result["time_str"] = f"~{h}h {m}m until full"
        elif energy_full and energy_now and power_now and power_now > 0:
            hrs = max(0, (energy_full - energy_now)) / power_now
            h = int(hrs)
            m = int((hrs - h) * 60)
            result["time_str"] = f"~{h}h {m}m until full"
    elif status_lower == "full":
        result["icon"] = "🔌"
        result["plugged_in"] = True
        result["time_str"] = "Fully Charged"

    return result


def get_uptime_str() -> str:
    """Retrieve human-readable system uptime from /proc/uptime."""
    try:
        with open("/proc/uptime", "r") as f:
            sec = float(f.read().split()[0])
            days = int(sec // 86400)
            hours = int((sec % 86400) // 3600)
            mins = int((sec % 3600) // 60)
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0 or days > 0:
                parts.append(f"{hours}h")
            parts.append(f"{mins}m")
            return " ".join(parts)
    except Exception:
        return "Unknown"


def get_load_average_str() -> str:
    """Read 1m, 5m, 15m load average from /proc/loadavg."""
    try:
        with open("/proc/loadavg", "r") as f:
            parts = f.read().split()
            if len(parts) >= 3:
                return f"{parts[0]}, {parts[1]}, {parts[2]}"
    except Exception:
        pass
    return "N/A"


def get_top_processes(limit: int = 3) -> str:
    """Get top CPU/Memory consuming processes."""
    try:
        res = subprocess.run(
            ["ps", "-eo", "comm,%cpu,%mem", "--sort=-%cpu"],
            capture_output=True,
            text=True,
            timeout=0.6,
        )
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()][1:]
            procs = []
            for line in lines[:limit]:
                parts = line.split()
                if len(parts) >= 3:
                    procs.append(f"{parts[0]} ({parts[1]}% CPU, {parts[2]}% RAM)")
            if procs:
                return ", ".join(procs)
    except Exception:
        pass
    return "N/A"


def get_system_telemetry() -> Dict[str, Any]:
    """Collect complete live system metrics."""
    distro = get_distro_info()
    cpu_temp = get_cpu_temp()
    ram = get_ram_usage()
    disk = get_disk_usage()
    battery = get_battery_status()
    uptime = get_uptime_str()
    load_avg = get_load_average_str()
    top_procs = get_top_processes(limit=3)
    uname = platform.uname()

    return {
        "distro": distro,
        "cpu_temp": cpu_temp,
        "ram": ram,
        "disk": disk,
        "battery": battery,
        "uptime": uptime,
        "load_avg": load_avg,
        "top_processes": top_procs,
        "kernel": f"{uname.release} ({uname.machine})",
    }


def get_live_system_snapshot() -> str:
    """
    Format a complete, real-time telemetry snapshot block for PETROVA's Brain prompt.
    Enables PETROVA to directly answer queries about battery, thermals, RAM, uptime, and load.
    """
    data = get_system_telemetry()
    temp_str = f"{data['cpu_temp']}°C" if data["cpu_temp"] else "N/A"
    
    battery_info = data["battery"]
    if battery_info["present"]:
        bat_str = f"{battery_info['percent']}% ({battery_info['status']}"
        if battery_info["time_str"]:
            bat_str += f", {battery_info['time_str']}"
        if battery_info["plugged_in"]:
            bat_str += ", AC Plugged In"
        else:
            bat_str += ", Running on Battery"
        bat_str += ")"
    else:
        bat_str = battery_info["status"]

    lines = [
        f"• Distribution: {data['distro']['pretty_name']} (Kernel {data['kernel']}, Pkg: {data['distro']['package_manager']}/{data['distro']['aur_helper']})",
        f"• CPU Temperature: {temp_str}",
        f"• RAM Usage: {data['ram']['used_gb']} GB / {data['ram']['total_gb']} GB ({data['ram']['pct']}%)",
        f"• Root Storage: {data['disk']['used_gb']} GB / {data['disk']['total_gb']} GB ({data['disk']['pct']}% used, {data['disk']['free_gb']} GB free)",
        f"• Battery & Power: {bat_str}",
        f"• System Uptime: {data['uptime']} | Load Average: {data['load_avg']}",
        f"• Top Active Processes: {data['top_processes']}",
    ]
    return "\n".join(lines)


def get_telemetry_bar() -> str:
    """Generate compact one-line telemetry status string for headers and response footers."""
    data = get_system_telemetry()
    temp_str = f"🌡️ {data['cpu_temp']}°C" if data["cpu_temp"] else "🌡️ N/A"
    ram_str = f"🧠 {data['ram']['used_gb']}/{data['ram']['total_gb']}GB ({data['ram']['pct']}%)"
    disk_str = f"💾 {data['disk']['used_gb']}/{data['disk']['total_gb']}GB ({data['disk']['pct']}%)"
    distro_str = f"🐧 {data['distro']['pretty_name']}"

    bat_str = ""
    if data["battery"]["present"] and data["battery"]["percent"] is not None:
        bat_icon = data["battery"]["icon"]
        bat_str = f"  •  {bat_icon} {data['battery']['percent']}%"

    return f"[dim]{distro_str}  •  {temp_str}  •  {ram_str}  •  {disk_str}{bat_str}[/dim]"

