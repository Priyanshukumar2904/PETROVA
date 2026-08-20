"""
Workspace & Local Project Intelligence Engine for PETROVA.
Auto-detects active git repositories, project frameworks, dependencies, and READMEs.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def get_git_info(cwd: Path) -> Dict[str, Any]:
    """Retrieve git repository branch, status, and origin."""
    info = {"is_git": False, "branch": "", "dirty": False, "origin": "", "modified_count": 0}

    if not (cwd / ".git").exists() and not (cwd.parent / ".git").exists():
        return info

    try:
        # Branch
        res = subprocess.run(["git", "branch", "--show-current"], cwd=str(cwd), capture_output=True, text=True, timeout=1.5)
        if res.returncode == 0 and res.stdout.strip():
            info["is_git"] = True
            info["branch"] = res.stdout.strip()

        # Status
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(cwd), capture_output=True, text=True, timeout=1.5)
        if status.returncode == 0:
            lines = [l for l in status.stdout.strip().split("\n") if l.strip()]
            info["modified_count"] = len(lines)
            info["dirty"] = len(lines) > 0

        # Remote
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=str(cwd), capture_output=True, text=True, timeout=1.5)
        if remote.returncode == 0:
            info["origin"] = remote.stdout.strip()

    except Exception:
        pass

    return info


def detect_project_type(cwd: Path) -> str:
    """Identify programming language and build system in the working directory."""
    types = []

    if (cwd / "pyproject.toml").exists() or (cwd / "requirements.txt").exists() or (cwd / "setup.py").exists():
        types.append("Python")
    if (cwd / "package.json").exists():
        types.append("Node.js/JavaScript")
    if (cwd / "Cargo.toml").exists():
        types.append("Rust")
    if (cwd / "go.mod").exists():
        types.append("Go")
    if (cwd / "CMakeLists.txt").exists() or (cwd / "Makefile").exists():
        types.append("C/C++")
    if (cwd / "Dockerfile").exists() or (cwd / "docker-compose.yml").exists():
        types.append("Docker")

    return ", ".join(types) if types else "General Directory"


def get_workspace_context() -> Dict[str, Any]:
    """Analyze current working directory and project files."""
    cwd = Path.cwd()
    git = get_git_info(cwd)
    proj_type = detect_project_type(cwd)

    readme_excerpt = ""
    readme_path = cwd / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                lines = [f.readline() for _ in range(25)]
                readme_excerpt = "".join(lines).strip()
        except Exception:
            pass

    return {
        "path": str(cwd),
        "folder_name": cwd.name,
        "git": git,
        "project_type": proj_type,
        "has_readme": bool(readme_excerpt),
        "readme_excerpt": readme_excerpt,
    }


def format_workspace_prompt_block() -> str:
    """Format workspace details for injection into system prompt."""
    ws = get_workspace_context()
    folder = ws["folder_name"]
    proj_type = ws["project_type"]

    parts = [f"Current Directory: {ws['path']} (Project: {folder}, Stack: {proj_type})"]

    if ws["git"]["is_git"]:
        branch = ws["git"]["branch"]
        dirty_str = f", {ws['git']['modified_count']} modified files" if ws["git"]["dirty"] else ", clean"
        parts.append(f"Git Repository: branch '{branch}'{dirty_str}")

    if ws["readme_excerpt"]:
        parts.append(f"Project Overview:\n{ws['readme_excerpt'][:350]}")

    return "\n".join(parts)
