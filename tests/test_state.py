"""Unit tests for PRISMA state and flow computation."""

import unittest
from src.prisma.flow_diagram import compute_prisma_flow_counts, generate_mermaid_flow_diagram
from src.prisma.checklist import evaluate_prisma_compliance


class TestPrismaState(unittest.TestCase):
    def test_prisma_flow_computation(self):
        mock_state = {
            "raw_studies": [
                {"id": "1", "source": "PubMed"},
                {"id": "2", "source": "arXiv"},
                {"id": "3", "source": "arXiv"},
            ],
            "deduplicated_studies": [
                {"id": "1", "source": "PubMed"},
                {"id": "2", "source": "arXiv"},
            ],
            "ta_screened_studies": [
                {"id": "1", "include_title_abstract": True},
                {"id": "2", "include_title_abstract": False},
            ],
            "fulltext_screened_studies": [
                {"id": "1", "include_full_text": True},
            ],
            "included_studies": [
                {"id": "1"},
            ]
        }
        counts = compute_prisma_flow_counts(mock_state)
        self.assertEqual(counts["total_identified"], 3)
        self.assertEqual(counts["duplicates_removed"], 1)
        self.assertEqual(counts["records_screened_ta"], 2)
        self.assertEqual(counts["records_excluded_ta"], 1)
        self.assertEqual(counts["final_included"], 1)

        mermaid = generate_mermaid_flow_diagram(counts)
        self.assertIn("IDENTIFICATION", mermaid)
        self.assertIn("SCREENING", mermaid)
        self.assertIn("INCLUDED", mermaid)

    def test_prisma_checklist_evaluation(self):
        sample_report = """
        # Systematic Literature Review
        ## Abstract
        ## Introduction & Rationale
        ## Eligibility criteria and search strategy on PubMed
        ## Screening and Selection Process
        ## Data Extraction
        ## Risk of bias assessment
        ## Results of synthesis
        ## Discussion & limitations
        ## Code on GitHub
        """
        counts = {"total_identified": 10}
        comp = evaluate_prisma_compliance(sample_report, counts)
        self.assertGreaterEqual(comp["score_percentage"], 70)
        self.assertIn(comp["status"], ["COMPLIANT", "PARTIALLY_COMPLIANT"])


if __name__ == "__main__":
    unittest.main()
