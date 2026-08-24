<p align="center">
  <img src="assets/petrova_banner.svg" alt="PETROVA Banner" width="100%" />
</p>

<p align="center">
  <b>Personal Enhanced Terminal Reasoning &amp; Operations Virtual Assistant</b><br>
  <i>An autonomous, privacy-first AI Operating Assistant and companion engineered natively for Linux.</i>
</p>

<p align="center">
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Platform-Linux-10b981?style=flat-square&logo=linux&logoColor=white" alt="Platform" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Python-3.10%2B-059669?style=flat-square&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Inference-llama.cpp%20%7C%20Ollama-f59e0b?style=flat-square" alt="Inference" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Storage-XDG%20%2B%20SQLite-10b981?style=flat-square" alt="Storage" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Privacy-100%25%20Local-34d399?style=flat-square" alt="Privacy" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-fbbf24?style=flat-square" alt="License" /></a>
</p>

---

## 🌟 Overview

**PETROVA** is an open-source, 100% local AI Operating Assistant designed natively for Linux power users and developers. It bridges local Large Language Models (LLMs) directly with your Linux environment, combining intelligent system tooling, real-time command execution, proactive hardware telemetry, desktop GUI visualization, voice interaction, and persistent long-term SQLite memory.

Unlike cloud chatbots that send telemetry and private shell interactions to remote servers, PETROVA runs **completely offline on your hardware**, keeps all preferences in your local XDG directory, and interfaces directly with local inference backends (`llama.cpp`, `Ollama`, or local OpenAI-compatible endpoints).

---

## ⚡ Interactive Terminal Walkthrough

<p align="center">
  <img src="assets/terminal_demo.svg" alt="PETROVA Terminal Walkthrough" width="100%" />
</p>

---

## 💎 Core Architecture & Capabilities

<p align="center">
  <img src="assets/features_showcase.svg" alt="PETROVA Features Showcase" width="100%" />
</p>

---

## 🚀 What's New in Recent Updates

* 🖥️ **PySide6 Neural Desktop App & HUD**: Native Wayland/X11 desktop GUI (`petrova-gui` or `/gui`) featuring an animated dynamic synaptic canvas, real-time telemetry gauges, and a slide-up embedded Linux terminal drawer.
* 🎙️ **Voice Interaction Subsystem**: High-speed offline Text-to-Speech (TTS) voice synthesis and microphone Speech-to-Text (STT) with hands-free push-to-talk (`/voice`, `/listen`).
* 🐧 **Deep Distro Precision & Awareness**: Automated detection for Arch Linux, CachyOS, Debian, and Fedora with native package manager formulation (`pacman`, `paru`, `cachyos-rate-mirrors`, `apt`, `dnf`) and zero cross-distro hallucinations.
* 🌟 **Proactive Health Briefings**: Welcomes you with contextual system greetings, live CPU thermals, RAM gauges, battery metrics, and continuity logs from previous sessions.
* 🎯 **Autonomous Multi-Step Goal Planner**: Type `/goal <task>` to decompose complex objectives into structured, interactive execution plans with live status indicators.

---

## ✨ Features Breakdown

### 🖥️ Dual-Mode Interface (CLI + GUI)
* **Modern Desktop GUI**: High-DPI, Wayland/X11 native application with live synaptic thought pulses, hardware telemetry, and `.desktop` application menu integration.
* **Interactive CLI Shell**: Built on `prompt_toolkit` and `Rich` with real-time token streaming, syntax highlighting, and smooth full-screen interactive TTY support (`htop`, `btop`, `vim`, `nano`).

### 🛡️ Safety & Privacy Guardrails
* **100% Offline & Local**: No data ever leaves your device.
* **Explain-Before-Execute**: High-risk commands (`rm -rf`, `dd`, `mkfs`, `chmod 777`) are automatically flagged with warning prompts regardless of permissions mode.
* **Credential Scrubbing**: Passwords, tokens, and private keys are detected and strictly excluded from long-term memory storage.

### 🧠 Persistent SQLite Memory
* **Context Continuity**: Remembers preferences, custom alias habits, and project notes across sessions (`~/.local/share/petrova/petrova.db`).
* **Configurable Storage Quotas**: Automated pruning and user-defined disk quotas (`/config memory <MB>`).

### 🌐 Live Web & Codebase Inspection
* **Zero-API Web Queries**: Perform real-time web lookups without external API keys (`/web <query>`).
* **GitHub Repo Fetcher**: Pass any GitHub repository URL (`https://github.com/...`) to automatically parse project structure, README documentation, and code files.

---

## 🔮 Upcoming Roadmap

Here is what is currently planned and in active development:

- [ ] 🧩 **Sidecar MCP Server & Custom Tools**: Support for Model Context Protocol (MCP) servers and user-written tool extensions.
- [ ] 👁️ **Multi-Modal Vision & Screen Capture**: Wayland/X11 screen region capture and OCR/vision reasoning for visual bug diagnostics and GUI troubleshooting.
- [ ] ⚡ **Global Quick-Summon HUD (`Super + Space`)**: Floating Raycast-style desktop overlay for instant keyboard-first queries anywhere across your desktop.
- [ ] 🔍 **Local Codebase RAG & Vector Search**: Automatic local project repository indexing and semantic code retrieval.
- [ ] ⏰ **Background System Daemon**: Proactive background alerts for thermal spikes, runaway processes, and low disk thresholds.

---

## 📦 Quick Start & Installation

### Option 1: Automated One-Step Install (Recommended)
```bash
git clone https://github.com/Priyanshukumar2904/PETROVA.git
cd PETROVA
chmod +x install.sh
./install.sh
```

### Option 2: Manual Setup
```bash
git clone https://github.com/Priyanshukumar2904/PETROVA.git
cd PETROVA
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Launching PETROVA
You can launch PETROVA through any of the following methods:
1. **Desktop Menu / Dock**: Click **PETROVA** in your desktop application launcher (GNOME, KDE Plasma, Rofi, Wofi).
2. **Terminal REPL**: Run `petrova` from any shell.
3. **Dedicated GUI Mode**: Run `petrova-gui` or `petrova --gui`.
4. **On-the-fly GUI Launch**: Inside the CLI shell, type `/gui` or `/app`.

---

## 📖 Command Reference Cheat Sheet

### 🖥️ Interface & Navigation
| Command | Description |
| :--- | :--- |
| **`/gui`** *(or `/app`)* | Launch the PySide6 Desktop GUI & Neural Visualizer |
| **`/voice`** | Toggle Voice Interaction Subsystem (STT / TTS) |
| **`/listen`** | Trigger one-shot microphone speech-to-text input |
| **`/clear`** | Clear terminal screen |
| **`/exit`** *(or `/quit`)* | Exit session (automatically records session journal) |

### ⚙️ System & Telemetry
| Command | Description |
| :--- | :--- |
| **`/stats`** | Display live CPU thermals, RAM gauges, and storage dashboard |
| **`/status`** | View live system health, AI server status, and permissions |
| **`/run <command>`** *(or `!<cmd>`)* | Safely execute a Linux shell command with duration metrics |
| **`/server start \| stop \| status`** | Manage local background inference supervisor (`llama-server`) |

### 🧠 Memory & Configuration
| Command | Description |
| :--- | :--- |
| **`/memory list`** | View all stored persistent memories and preferences |
| **`/memory search <query>`** | Search stored memories by keyword relevance |
| **`/memory add <fact>`** | Manually store a persistent memory item |
| **`/memory delete <id>`** | Delete a specific memory item by ID |
| **`/config view`** | View all active configurations and settings |
| **`/config permissions`** | Switch execution mode (`confirm`, `autonomous`, `read_only`) |
| **`/config memory <mb>`** | Adjust SQLite database storage quota cap in MB |
| **`/setup`** *(or `/config reset`)* | Re-run the interactive 4-step onboarding wizard |

### 🌐 Goals & Intelligence
| Command | Description |
| :--- | :--- |
| **`/goal <objective>`** | Plan and execute a multi-step agentic objective with live progress |
| **`/fetch <url>`** | Fetch and inspect any live web page or GitHub repository |
| **`/web <query>`** | Search the web without needing external API keys |
| **`/help`** | Display complete interactive command reference |

---

## 🏗️ Architecture Overview

<p align="center">
  <img src="assets/architecture.svg" alt="PETROVA Architecture Diagram" width="100%" />
</p>

### 💡 How It Works in 4 Simple Steps

```
[ You (GUI / Terminal / Voice) ]
               │
               ▼
[ 1. Central Intelligence Router ]  ── (Directs your request to the right engine)
               │
               ▼
[ 2. Offline AI Brain & Safety Shield ] ── (Thinks 100% locally & checks commands)
               │
               ▼
[ 3. Local SQLite Memory Vault ] ── (Remembers your habits & preferences)
```

1. **How You Connect (The Senses)**: You interact through your preferred interface — the **Desktop GUI**, lightning-fast **Terminal REPL**, or hands-free **Voice Engine**.
2. **The Central Router (The Traffic Director)**: Identifies whether your input is an AI question, a Linux shell command, or a multi-step objective, routing it with zero lag.
3. **The Brain & Safety Shield (Thinking & Doing)**:
   * **100% Offline AI Brain**: Runs local LLMs on your GPU/CPU with no internet required.
   * **Safety Guardrails**: Inspects every command beforehand and asks for your confirmation before executing anything destructive.
   * **Agentic Planner**: Automatically breaks big goals down into an interactive step-by-step checklist.
4. **The Local Memory Vault (Remembering)**: Stores your preferences, shell habits, and session journals in a fast SQLite database located at `~/.local/share/petrova/`.

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

Developed with ❤️ by [Priyanshukumar2904](https://github.com/Priyanshukumar2904).

