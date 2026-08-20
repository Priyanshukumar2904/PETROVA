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
)
from petrova.memory.manager import extract_explicit_memory, extract_heuristic_facts
from petrova.brain.prompt import build_system_prompt
from petrova.core.router import route_command


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
        # Save memories
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

    def test_memory_extraction_heuristics(self):
        explicit = extract_explicit_memory("remember that I use Zsh shell")
        self.assertIsNotNone(explicit)
        self.assertEqual(explicit[0], "I use Zsh shell")

        heuristic = extract_heuristic_facts("my preferred editor is VS Code")
        self.assertIsNotNone(heuristic)
        self.assertEqual(heuristic[1], "preference")

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
