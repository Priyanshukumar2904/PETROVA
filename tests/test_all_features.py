"""
Comprehensive Verification Suite for PETROVA Core Features.
Tests:
1. Memory Retention & SQLite Quotas
2. Command Execution & Safety Guardrails
3. Linux Distro Intelligence & Hardware Telemetry
4. Proactive Health Briefings & Continuity Journals
5. Voice Subsystem Profiles & Configuration
6. Slash Command Routing
"""

import os
import sys
import unittest

from petrova.config.settings import get_config
from petrova.memory.store import (
    initialize,
    save_memory,
    get_all_memories,
    search_memories,
    delete_memory_by_id,
    log_session_summary,
    get_last_session_summary,
    get_db_size_mb,
    get_memory_count,
    enforce_storage_quota,
)
from petrova.tools.executor import is_potentially_dangerous, is_interactive, execute_command
from petrova.linux.stats import get_distro_info, get_system_telemetry
from petrova.ui.greeting import get_greeting
from petrova.brain.prompt import build_system_prompt
from petrova.voice.tts import VOICE_PROFILES, get_current_voice, set_current_voice, clean_text_for_speech
from petrova.core.router import route_command


class TestPetrovaFeatures(unittest.TestCase):

    def setUp(self):
        self.config = get_config()

    # ---------------- 1. MEMORY RETENTION ----------------
    def test_01_memory_crud_and_retention(self):
        """Verify memory insertion, search, retrieval, and deletion."""
        initialize()
        
        # Add test memory
        saved = save_memory("User prefers dark mode and uses neovim as primary editor.", category="preference")
        self.assertTrue(saved)

        # Retrieve and verify presence
        all_mems = get_all_memories()
        found = any("neovim" in m["content"] for m in all_mems)
        self.assertTrue(found, "Memory was not retained in SQLite database.")

        # Search memory
        results = search_memories("neovim")
        self.assertTrue(len(results) > 0, "Memory search by keyword failed.")
        self.assertIn("neovim", results[0]["content"])
        mem_id = results[0]["id"]

        # Delete test memory
        deleted = delete_memory_by_id(mem_id)
        self.assertTrue(deleted)
        post_del = search_memories("neovim")
        self.assertEqual(len(post_del), 0, "Memory deletion failed.")

    def test_02_episodic_session_journal(self):
        """Verify session continuity journals."""
        log_session_summary("Worked on optimizing Linux kernel modules and cleaned cache.", commands_run=3)
        last_journal = get_last_session_summary()
        self.assertIsNotNone(last_journal)
        self.assertIn("kernel modules", last_journal["summary"])
        self.assertEqual(last_journal["commands_run"], 3)

    def test_03_memory_quota_stats(self):
        """Verify storage quota enforcement and statistics."""
        count = get_memory_count()
        self.assertIsInstance(count, int)
        size_mb = get_db_size_mb()
        self.assertGreaterEqual(size_mb, 0.0)
        enforce_storage_quota()

    # ---------------- 2. COMMAND EXECUTION & SAFETY ----------------
    def test_04_dangerous_command_detection(self):
        """Verify high-risk command security guardrails."""
        dangerous_cases = [
            "rm -rf /",
            "sudo rm -rf /*",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/nvme0n1",
            ":(){ :|:& };:",
            "chmod -R 777 /",
        ]
        for cmd in dangerous_cases:
            self.assertTrue(is_potentially_dangerous(cmd), f"Failed to flag dangerous command: {cmd}")

        safe_cases = [
            "ls -la",
            "uname -r",
            "git status",
            "free -h",
            "cat /etc/os-release",
        ]
        for cmd in safe_cases:
            self.assertFalse(is_potentially_dangerous(cmd), f"Incorrectly flagged safe command: {cmd}")

    def test_05_interactive_tui_detection(self):
        """Verify detection of full-screen interactive tools (htop, vim, top)."""
        self.assertTrue(is_interactive("htop"))
        self.assertTrue(is_interactive("vim file.txt"))
        self.assertTrue(is_interactive("nano test.py"))
        self.assertTrue(is_interactive("top"))
        self.assertFalse(is_interactive("ls -lh"))

    def test_06_safe_command_execution(self):
        """Verify safe execution of standard commands with duration & exit codes."""
        orig_mode = self.config.get("permission_mode", "confirm")
        try:
            self.config.set("permission_mode", "autonomous")
            exit_code, stdout, stderr = execute_command("echo 'PETROVA_TEST_OK'")
            self.assertEqual(exit_code, 0)
            self.assertIn("PETROVA_TEST_OK", stdout)
        finally:
            self.config.set("permission_mode", orig_mode)

    # ---------------- 3. DISTRO PRECISION & HARDWARE TELEMETRY ----------------
    def test_07_distro_precision(self):
        """Verify Linux distribution detection."""
        distro = get_distro_info()
        self.assertIsNotNone(distro)
        self.assertIn("pretty_name", distro)

    def test_08_hardware_telemetry(self):
        """Verify CPU, RAM, battery, and disk telemetry."""
        telemetry = get_system_telemetry()
        self.assertIn("ram", telemetry)
        self.assertIn("used_gb", telemetry["ram"])
        self.assertIn("total_gb", telemetry["ram"])
        self.assertIn("pct", telemetry["ram"])
        self.assertIn("disk", telemetry)
        self.assertIn("battery", telemetry)

    # ---------------- 4. BEHAVIORAL FEATURES & BRIEFINGS ----------------
    def test_09_proactive_briefing(self):
        """Verify proactive greetings and system briefings."""
        greeting = get_greeting()
        self.assertIsNotNone(greeting)
        self.assertTrue(len(greeting) > 5)

    def test_10_distro_aware_system_prompt(self):
        """Verify system prompt includes distro intelligence and memory context."""
        prompt = build_system_prompt()
        self.assertIn("PETROVA", prompt)
        self.assertIn("Linux", prompt)

    # ---------------- 5. VOICE SUBSYSTEM ----------------
    def test_11_voice_profiles_and_switching(self):
        """Verify voice profiles catalog and speed settings."""
        self.assertIn("nova", VOICE_PROFILES)
        self.assertIn("echo", VOICE_PROFILES)
        self.assertIn("jenny", VOICE_PROFILES)
        self.assertIn("onyx", VOICE_PROFILES)
        self.assertIn("sonia", VOICE_PROFILES)
        self.assertIn("ryan", VOICE_PROFILES)
        self.assertIn("nat", VOICE_PROFILES)

        # Test switching
        set_current_voice("onyx")
        self.assertEqual(get_current_voice(), "onyx")
        set_current_voice("nova")
        self.assertEqual(get_current_voice(), "nova")

    def test_12_speech_cleaning(self):
        """Verify stripping of markdown, code blocks, links from speech."""
        text = "Hello! Check `pacman -Syu` and see ```bash\nsudo rm -rf /tmp\n``` or visit https://github.com"
        clean = clean_text_for_speech(text)
        self.assertNotIn("```", clean)
        self.assertNotIn("https://", clean)
        self.assertIn("pacman -Syu", clean)

    # ---------------- 6. SLASH COMMAND ROUTER ----------------
    def test_13_slash_commands_routing(self):
        """Verify slash commands execute and return cleanly."""
        self.assertTrue(route_command("/stats"))
        self.assertTrue(route_command("/status"))
        self.assertTrue(route_command("/memory list"))
        self.assertTrue(route_command("/voice status"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
