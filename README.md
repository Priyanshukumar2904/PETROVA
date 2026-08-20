<p align="center">
  <img src="assets/petrova_banner.svg" alt="PETROVA Banner" width="100%" />
</p>

<p align="center">
  <b>Personal Enhanced Terminal Reasoning & Operations Virtual Assistant</b>
</p>

<p align="center">
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Platform-Linux-blue?style=flat-square&logo=linux" alt="Platform" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python" alt="Python" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Inference-llama.cpp%20%7C%20Ollama-orange?style=flat-square" alt="Inference" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Storage-XDG%20%2B%20SQLite-10B981?style=flat-square" alt="Storage" /></a>
  <a href="https://github.com/Priyanshukumar2904/PETROVA"><img src="https://img.shields.io/badge/Privacy-100%25%20Local-purple?style=flat-square" alt="Privacy" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" /></a>
</p>

---

## 🌟 Overview

**PETROVA** is an open-source, privacy-first AI Operating Assistant designed for Linux. It combines local Large Language Models (LLMs), intelligent system tooling, real-time command execution, and persistent long-term SQLite memory to help you understand, maintain, diagnose, and automate your Linux system.

Unlike cloud chatbots that send your data across the internet, PETROVA runs **100% locally on your machine**, keeps your history private, and directly connects to local inference backends (`llama.cpp`, `Ollama`, or OpenAI-compatible APIs).

---

## 🎬 Live Terminal Demo

<p align="center">
  <img src="assets/terminal_demo.svg" alt="PETROVA Interactive Terminal Demo" width="100%" />
</p>

---

## ✨ Key Features

- 🚀 **1-Command Global Startup**: Launch your assistant from any terminal prompt simply by typing `petrova`.
- 🧙‍♂️ **One-Time Onboarding Wizard**: Effortlessly choose your preferred name, model tier, terminal permissions, and memory storage quota on first launch.
- ⚡ **Interactive Command Execution**: Ask PETROVA to perform operations (e.g. *“update my system”*, *“clean disk cache”*, *“diagnose open ports”*). PETROVA proposes the exact bash command and safely prompts `[y/N]` before executing.
- 🧠 **Persistent SQLite Memory**: Remembers user preferences, project notes, and shell habits across sessions with automated storage quota caps (`~/.local/share/petrova/petrova.db`).
- 🌐 **Live Web & GitHub Inspector**: Pass any URL or GitHub repo link (`https://github.com/...`) in chat or via `/fetch`, and PETROVA will analyze the live repository structure and README.
- 🏎️ **Zero-Latency Token Streaming**: Real-time SSE token streaming renders responses instantly token-by-token with zero terminal freezing.

---

## 🚀 Quick Start & Installation

### Option 1: One-Step Automated Install (Recommended)
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
From **any terminal window** on your system, simply run:
```bash
petrova
```

---

## 📖 Built-in Slash Commands

| Command | Description |
| :--- | :--- |
| **`/help`** | Display complete command reference table |
| **`/run <command>`** *(or `!<cmd>`)* | Safely execute a Linux shell command with live duration metrics |
| **`/fetch <url>`** | Fetch and inspect any live web page or GitHub repository |
| **`/web <query>`** | Search the web without needing external API keys |
| **`/status`** | View live system health, AI server, permissions, and memory usage |
| **`/config view`** | View all active configurations and settings |
| **`/config name <name>`** | Change the name PETROVA addresses you by |
| **`/config permissions`** | Switch execution mode (`confirm`, `autonomous`, `read_only`) |
| **`/config memory <mb>`** | Adjust SQLite database storage quota cap in MB |
| **`/setup`** *(or `/config reset`)* | Re-run the full 4-step onboarding wizard |
| **`/memory list`** | View all stored persistent memories and preferences |
| **`/memory search <query>`** | Search stored memories by keyword relevance |
| **`/memory add <fact>`** | Manually store a persistent memory item |
| **`/memory delete <id>`** | Delete a specific memory item by ID |
| **`/server start \| stop \| status`** | Manage local background AI inference supervisor |
| **`/clear`** | Clear terminal screen |
| **`/exit`** *(or `/quit`)* | Exit session |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Terminal["🖥️ Interactive CLI Interface"]
        A["prompt_toolkit REPL & Shell"]
        B["Rich Terminal & Status UI"]
        C["Slash Command Router"]
    end

    subgraph Core["⚙️ PETROVA Brain & Engine"]
        D["System Context & Action Prompt Builder"]
        E["Token Streaming Provider"]
        F["Process Supervisor (llama-server / Ollama)"]
        G["Safe Command Executor (Timeout & Safety Rules)"]
        H["Web & GitHub Inspector"]
    end

    subgraph Storage["💾 XDG Storage Standard"]
        I["Config: ~/.config/petrova/config.json"]
        J["Memory DB: ~/.local/share/petrova/petrova.db"]
        K["History: ~/.local/share/petrova/history"]
    end

    A --> C
    C -->|Slash Commands| B
    C -->|Run Shell Command| G
    C -->|Web / GitHub Query| H
    A -->|AI Question| D
    D --> E
    D <--> H
    E <-->|Inference| F
    D <-->|Memory Retrieval| J
    A <--> I
    A <--> K
```

---

## 🛡️ Privacy & Security

* **100% Local Inference**: Your prompts, shell inputs, and file data stay entirely on your device.
* **Explain-Before-Execute**: High-risk destructive commands (`rm -rf`, `mkfs`, `dd`, `chmod 777`) are automatically flagged with warning prompts regardless of autonomy mode.
* **Credential Scrubbing**: Passwords, API tokens, and private keys are detected and strictly discarded from persistent memory storage.

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

Developed with ❤️ by [Priyanshukumar2904](https://github.com/Priyanshukumar2904).
