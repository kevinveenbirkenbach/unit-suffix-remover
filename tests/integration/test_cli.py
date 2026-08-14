import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"


def run_cli(*args, path=None):
    """Run 'python -m unit_suffix_remover' with the working tree on PYTHONPATH.

    Args:
        args: Command line arguments for the CLI.
        path: Replacement PATH, used to hide the systemctl binary.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR)
    if path is not None:
        env["PATH"] = str(path)
    return subprocess.run(
        [sys.executable, "-m", "unit_suffix_remover", *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


class TestCli(unittest.TestCase):
    def test_dry_run_keeps_the_unit_file(self):
        with tempfile.TemporaryDirectory() as base:
            unit = os.path.join(base, "web.infinito.service")
            with open(unit, "w") as handle:
                handle.write("")

            result = run_cli("-s", "infinito", "--unit-dir", base, "--dry-run")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Would remove file", result.stdout)
            self.assertTrue(os.path.exists(unit))

    def test_reports_when_nothing_matches(self):
        with tempfile.TemporaryDirectory() as base:
            result = run_cli("-s", "infinito", "--unit-dir", base)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No matching units found.", result.stdout)

    def test_suffix_is_required(self):
        result = run_cli("--unit-dir", "/tmp")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--suffix", result.stderr)

    def test_missing_systemctl_fails_cleanly(self):
        with (
            tempfile.TemporaryDirectory() as base,
            tempfile.TemporaryDirectory() as empty,
        ):
            with open(os.path.join(base, "web.infinito.service"), "w") as handle:
                handle.write("")

            result = run_cli("-s", "infinito", "--unit-dir", base, path=empty)

        self.assertEqual(result.returncode, 127)
        self.assertIn("required command 'systemctl' is not installed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
