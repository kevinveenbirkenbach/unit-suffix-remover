import os
import tempfile
import unittest
from unittest import mock

from unit_suffix_remover.core import (
    REQUIRED_BINARIES,
    MissingBinaryError,
    has_exact_suffix,
    iter_matching_units,
    process_unit,
    systemctl,
)


class TestHasExactSuffix(unittest.TestCase):
    def test_accept(self):
        ok = [
            "a.infinito.service",
            "a.infinito.timer",
            "a.infinito@.service",
            "a.infinito@.timer",
            "a.infinito@x.service",
            "a.b-c_d.infinito@inst.timer",
        ]
        for name in ok:
            with self.subTest(name=name):
                self.assertTrue(has_exact_suffix(name, "infinito"))

    def test_reject(self):
        bad = [
            "a.infinito.nexus.timer",
            "a@inst.infinito.timer",
            "a.infinitoX.service",
            "a.service",
            "a.timer",
            "infinito.service",
            "a.infinito@/weird.service",
        ]
        for name in bad:
            with self.subTest(name=name):
                self.assertFalse(has_exact_suffix(name, "infinito"))

    def test_dot_in_suffix_is_not_a_wildcard(self):
        self.assertTrue(has_exact_suffix("a.inf.nito.service", "inf.nito"))
        self.assertFalse(has_exact_suffix("a.infXnito.service", "inf.nito"))


class TestIterMatchingUnits(unittest.TestCase):
    def _touch(self, base, name):
        path = os.path.join(base, name)
        with open(path, "w") as handle:
            handle.write("")
        return path

    def test_matches_only_units_with_suffix(self):
        with tempfile.TemporaryDirectory() as base:
            wanted = self._touch(base, "web.infinito.service")
            self._touch(base, "web.other.service")
            self._touch(base, "web.infinito.conf")

            self.assertEqual(list(iter_matching_units(base, "infinito")), [wanted])

    def test_skips_directories(self):
        with tempfile.TemporaryDirectory() as base:
            os.mkdir(os.path.join(base, "web.infinito.service"))

            self.assertEqual(list(iter_matching_units(base, "infinito")), [])

    def test_missing_directory_yields_nothing(self):
        self.assertEqual(list(iter_matching_units("/nonexistent/units", "x")), [])


class TestSystemctl(unittest.TestCase):
    def test_quiet_discards_output(self):
        with mock.patch("unit_suffix_remover.core.subprocess.run") as run:
            run.return_value.returncode = 0
            systemctl("stop", "a.service")

        kwargs = run.call_args.kwargs
        self.assertEqual(run.call_args.args[0], ["systemctl", "stop", "a.service"])
        self.assertIn("stdout", kwargs)
        self.assertIn("stderr", kwargs)

    def test_loud_keeps_output(self):
        with mock.patch("unit_suffix_remover.core.subprocess.run") as run:
            run.return_value.returncode = 0
            systemctl("daemon-reload", quiet=False)

        self.assertNotIn("stdout", run.call_args.kwargs)

    def test_missing_systemctl_raises_missing_binary(self):
        with mock.patch("unit_suffix_remover.core.subprocess.run") as run:
            run.side_effect = FileNotFoundError

            with self.assertRaises(MissingBinaryError) as caught:
                systemctl("stop", "a.service")

        self.assertEqual(caught.exception.binary, "systemctl")


class TestRequiredBinaries(unittest.TestCase):
    def test_declares_every_external_command_the_package_calls(self):
        self.assertEqual(set(REQUIRED_BINARIES), {"systemctl"})


class TestProcessUnit(unittest.TestCase):
    def test_dry_run_touches_nothing(self):
        with tempfile.TemporaryDirectory() as base:
            path = os.path.join(base, "web.infinito.service")
            with open(path, "w") as handle:
                handle.write("")

            with mock.patch("unit_suffix_remover.core.systemctl") as systemctl_mock:
                process_unit(path, dry_run=True)

            systemctl_mock.assert_not_called()
            self.assertTrue(os.path.exists(path))

    def test_stops_disables_and_removes(self):
        with tempfile.TemporaryDirectory() as base:
            path = os.path.join(base, "web.infinito.service")
            with open(path, "w") as handle:
                handle.write("")

            with mock.patch("unit_suffix_remover.core.systemctl") as systemctl_mock:
                process_unit(path)

            self.assertEqual(
                [call.args for call in systemctl_mock.call_args_list],
                [
                    ("stop", "web.infinito.service"),
                    ("disable", "web.infinito.service"),
                ],
            )
            self.assertFalse(os.path.exists(path))

    def test_missing_file_is_tolerated(self):
        with mock.patch("unit_suffix_remover.core.systemctl"):
            process_unit("/nonexistent/web.infinito.service")


if __name__ == "__main__":
    unittest.main()
