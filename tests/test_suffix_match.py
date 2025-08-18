# tests/test_suffix_match.py
import unittest
from main import has_exact_suffix

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
        for f in ok:
            with self.subTest(f=f):
                self.assertTrue(has_exact_suffix(f, "infinito"))

    def test_reject(self):
        bad = [
            "a.infinito.nexus.timer",
            "a@inst.infinito.timer",
            "a.infinitoX.service",
            "a.service", "a.timer",
            "infinito.service",   # no prefix before suffix token
            "a.infinito@/weird.service", # unlikely but protects against pathy chars
        ]
        for f in bad:
            with self.subTest(f=f):
                self.assertFalse(has_exact_suffix(f, "infinito"))

if __name__ == "__main__":
    unittest.main()
