"""Unit tests for tool functions and fallback handling."""

import unittest
from src.tools.pubmed import parse_pubmed_xml
from src.tools.dedup import normalize_title


class TestTools(unittest.TestCase):
    def test_normalize_title_empty(self):
        self.assertEqual(normalize_title(""), "")
        self.assertEqual(normalize_title(None), "")

    def test_pubmed_xml_empty(self):
        self.assertEqual(parse_pubmed_xml(b"<empty></empty>"), [])


if __name__ == "__main__":
    unittest.main()
