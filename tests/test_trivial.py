"""Trivial tests."""

import inspect
import unittest

from more_click import debug_option


class TestTrivial(unittest.TestCase):
    """A trivial test case."""

    def test_option(self):
        """Test types."""
        self.assertTrue(inspect.isfunction(debug_option))
