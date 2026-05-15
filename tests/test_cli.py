from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_cli_creates_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = [
                sys.executable,
                "-m",
                "codefortify_starter",
                "demo_cli",
                "--no-git",
                "--directory",
                str(root),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue((root / "demo_cli" / "manage.py").exists())

    def test_cli_invalid_name_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = [
                sys.executable,
                "-m",
                "codefortify_starter",
                "123invalid",
                "--directory",
                str(root),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Error:", result.stdout)

    def test_cli_existing_folder_requires_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "demo_exists").mkdir()

            fail_command = [
                sys.executable,
                "-m",
                "codefortify_starter",
                "demo_exists",
                "--no-git",
                "--directory",
                str(root),
            ]
            fail_result = subprocess.run(fail_command, capture_output=True, text=True, check=False)
            self.assertEqual(fail_result.returncode, 1)

            force_command = fail_command + ["--force"]
            force_result = subprocess.run(force_command, capture_output=True, text=True, check=False)
            self.assertEqual(force_result.returncode, 0, msg=force_result.stderr)
            self.assertTrue((root / "demo_exists" / "manage.py").exists())

