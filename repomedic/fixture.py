"""One reproducible bug fixture; never execute a user-supplied repository."""
from pathlib import Path

BUGGY = 'def eligible_for_free_shipping(total: float, threshold: float = 50.0) -> bool:\n    """Free shipping applies at and above the threshold."""\n    return total > threshold\n'
FIXED = 'def eligible_for_free_shipping(total: float, threshold: float = 50.0) -> bool:\n    """Free shipping applies at and above the threshold."""\n    return total >= threshold\n'
TEST_FILE = 'import unittest\nfrom shipping import eligible_for_free_shipping\n\nclass ShippingTests(unittest.TestCase):\n    def test_below(self):\n        self.assertFalse(eligible_for_free_shipping(49.99))\n\n    def test_boundary(self):\n        self.assertTrue(eligible_for_free_shipping(50.0))\n\n    def test_above(self):\n        self.assertTrue(eligible_for_free_shipping(50.01))\n\n    def test_custom_threshold(self):\n        self.assertTrue(eligible_for_free_shipping(20.0, 20.0))\n\nif __name__ == "__main__":\n    unittest.main()\n'

def install_fixture(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "shipping.py").write_text(BUGGY, encoding="utf-8")
    (directory / "test_shipping.py").write_text(TEST_FILE, encoding="utf-8")
