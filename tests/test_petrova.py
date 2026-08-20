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
from petrova.memory.decision import evaluate_memory_candidate
from petrova.brain.prompt import build_system_prompt
from petrova.brain.brain import extract_urls, extract_suggested_commands
from petrova.core.router import route_command
from petrova.tools.executor import is_potentially_dangerous, is_readonly_safe
from petrova.tools.web import clean_html


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

        results = search_memories("Neovim")
        self.assertGreater(len(results), 0)
        self.assertIn("Neovim", results[0]["content"])

        prefs = get_all_memories(category="preference")
        self.assertEqual(len(prefs), 1)

        delete_memory("Prefers Neovim for coding")
        self.assertEqual(get_memory_count(), 2)

    def test_memory_decision_matrix(self):
        should, _, _, _ = evaluate_memory_candidate("hello petrova")
        self.assertFalse(should)

        should, _, _, _ = evaluate_memory_candidate("my api_key = 'sk-1234567890'")
        self.assertFalse(should)

        should, cat, imp, content = evaluate_memory_candidate("remember that I use Docker for microservices")
        self.assertTrue(should)
        self.assertEqual(content, "I use Docker for microservices")

    def test_tool_safety_classification(self):
        self.assertTrue(is_potentially_dangerous("rm -rf /"))
        self.assertTrue(is_potentially_dangerous("mkfs.ext4 /dev/sda1"))
        self.assertFalse(is_potentially_dangerous("uname -r"))

        self.assertTrue(is_readonly_safe("uname -a"))
        self.assertTrue(is_readonly_safe("df -h"))
        self.assertFalse(is_readonly_safe("rm test.txt"))

    def test_interactive_and_normalization(self):
        from petrova.tools.executor import is_interactive, normalize_command
        self.assertTrue(is_interactive("htop"))
        self.assertTrue(is_interactive("sudo htop"))
        self.assertTrue(is_interactive("vim /etc/fstab"))
        self.assertTrue(is_interactive("btop"))
        self.assertFalse(is_interactive("ls -la"))

        self.assertEqual(normalize_command("h top"), "htop")
        self.assertEqual(normalize_command("fast fetch"), "fastfetch")


    def test_command_and_url_extraction(self):
        # Command extraction
        response = "Run this:\n```bash\nsudo pacman -Syu\n```"
        cmds = extract_suggested_commands(response)
        self.assertIn("sudo pacman -Syu", cmds)

        # URL extraction
        text = "Check out https://github.com/Priyanshukumar2904/PETROVA and https://google.com"
        urls = extract_urls(text)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://github.com/Priyanshukumar2904/PETROVA", urls)

    def test_html_cleaner(self):
        html = "<html><body><h1>Title</h1><p>Paragraph text.</p><script>evil()</script></body></html>"
        cleaned = clean_html(html)
        self.assertIn("Title", cleaned)
        self.assertIn("Paragraph text.", cleaned)
        self.assertNotIn("evil()", cleaned)

    def test_system_prompt_builder(self):
        memories = [{"content": "User prefers concise answers."}]
        prompt = build_system_prompt(memories)
        self.assertIn("PETROVA", prompt)
        self.assertIn("User prefers concise answers.", prompt)

    def test_voice_cleaner_and_workspace(self):
        from petrova.voice.tts import clean_text_for_speech
        from petrova.linux.workspace import get_workspace_context
        
        sample = "Here is a command: ```bash\nsudo pacman -Syu\n```\nVisit https://cachyos.org today!"
        cleaned = clean_text_for_speech(sample)
        self.assertNotIn("sudo pacman -Syu", cleaned)
        self.assertNotIn("https://cachyos.org", cleaned)
        self.assertIn("command proposed", cleaned)

        ws = get_workspace_context()
        self.assertIsNotNone(ws["folder_name"])
        self.assertIn("project_type", ws)

    def test_command_routing(self):
        self.assertTrue(route_command("/help"))
        self.assertTrue(route_command("/version"))
        self.assertTrue(route_command("/about"))
        self.assertFalse(route_command("What is the kernel version?"))



if __name__ == "__main__":
    unittest.main()
