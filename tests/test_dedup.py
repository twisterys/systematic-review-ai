"""Unit tests for deduplication module."""

import unittest
from src.tools.dedup import deduplicate_studies, normalize_title, is_title_duplicate


class TestDedup(unittest.TestCase):
    def test_normalize_title(self):
        t1 = "Cognitive Multi-Agent Ecosystems: A Review!"
        self.assertEqual(normalize_title(t1), "cognitive multiagent ecosystems a review")

    def test_is_title_duplicate(self):
        t1 = "Multi-Agent System for Autonomous Talent Marketplaces"
        t2 = "Multi-Agent Systems for Autonomous Talent Marketplaces"
        self.assertTrue(is_title_duplicate(t1, t2))

    def test_deduplicate_studies(self):
        studies = [
            {"id": "1", "title": "AI in Talent Matching", "doi": "10.1000/182"},
            {"id": "2", "title": "AI in Talent Matching (Duplicate)", "doi": "10.1000/182"},
            {"id": "3", "title": "AI in Talent Matching.", "doi": ""},
            {"id": "4", "title": "A Different Paper on Autonomous Agents", "doi": "10.1000/183"}
        ]
        deduped, removed = deduplicate_studies(studies)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(removed, 2)


if __name__ == "__main__":
    unittest.main()
