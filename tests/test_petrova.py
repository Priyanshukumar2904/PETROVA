"""
Unit and Integration Tests for PETROVA Core Systems.
"""

import unittest
from petrova.config.settings import get_config, Config
from petrova.memory.store import (
    initialize,
    save_memory,
    get_memories,
    search_memories,
    get_all_memories,
    delete_memory,
    clear_all_memories,
    get_memory_count,
    enforce_storage_quota,
)
from petrova.memory.decision import evaluate_memory_candidate, is_sensitive, is_ephemeral
from petrova.memory.manager import process_memory
from petrova.brain.prompt import build_system_prompt
from petrova.core.router import route_command
from petrova.tools.executor import is_potentially_dangerous, is_readonly_safe


class TestPetrovaCore(unittest.TestCase):
    def setUp(self):
        initialize()
        clear_all_memories()

    def tearDown(self):
        clear_all_memories()

    def test_config_initialization(self):
        config = get_config()
        self.assertIsNotNone(config.user_name)
        self.assertIsNotNone(config.backend)
        self.assertIsNotNone(config.server_url)

    def test_memory_crud_and_search(self):
        save_memory("Prefers Neovim for coding", category="preference", importance=5)
        save_memory("Primary workstation running Arch Linux", category="configuration", importance=4)
        save_memory("Project PETROVA repository is open source", category="project", importance=3)

        self.assertEqual(get_memory_count(), 3)

        # Search memory
        results = search_memories("Neovim")
        self.assertGreater(len(results), 0)
        self.assertIn("Neovim", results[0]["content"])

        # Category retrieval
        prefs = get_all_memories(category="preference")
        self.assertEqual(len(prefs), 1)

        # Deletion
        delete_memory("Prefers Neovim for coding")
        self.assertEqual(get_memory_count(), 2)

    def test_memory_decision_matrix(self):
        # 1. Ephemeral banter should be ignored
        should, cat, _, _ = evaluate_memory_candidate("hello petrova")
        self.assertFalse(should)

        # 2. Secret passwords should be discarded
        should, _, _, _ = evaluate_memory_candidate("my api_key = 'sk-1234567890'")
        self.assertFalse(should)

        # 3. Explicit directive should be remembered
        should, cat, imp, content = evaluate_memory_candidate("remember that I use Docker for microservices")
        self.assertTrue(should)
        self.assertEqual(content, "I use Docker for microservices")

        # 4. Natural preference declaration
        should, cat, _, _ = evaluate_memory_candidate("my favorite shell is zsh")
        self.assertTrue(should)
        self.assertEqual(cat, "preference")

    def test_tool_safety_classification(self):
        self.assertTrue(is_potentially_dangerous("rm -rf /"))
        self.assertTrue(is_potentially_dangerous("mkfs.ext4 /dev/sda1"))
        self.assertFalse(is_potentially_dangerous("uname -r"))

        self.assertTrue(is_readonly_safe("uname -a"))
        self.assertTrue(is_readonly_safe("df -h"))
        self.assertFalse(is_readonly_safe("rm test.txt"))

    def test_system_prompt_builder(self):
        memories = [{"content": "User prefers concise answers."}]
        prompt = build_system_prompt(memories)
        self.assertIn("PETROVA", prompt)
        self.assertIn("User prefers concise answers.", prompt)

    def test_command_routing(self):
        self.assertTrue(route_command("/help"))
        self.assertTrue(route_command("/version"))
        self.assertTrue(route_command("/about"))
        self.assertFalse(route_command("What is the kernel version?"))


if __name__ == "__main__":
    unittest.main()
