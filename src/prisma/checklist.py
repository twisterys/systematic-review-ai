"""
PRISMA 2020 Checklist validator and auditor.
Evaluates the systematic review against PRISMA items to ensure compliance.
"""

from typing import Dict, Any, List

PRISMA_2020_SECTIONS = {
    "TITLE": ["Item 1: Title identifying the report as a systematic review"],
    "ABSTRACT": ["Item 2: Structured summary abstract"],
    "INTRODUCTION": [
        "Item 3: Rationale in the context of existing knowledge",
        "Item 4: Explicit statement of questions or objectives"
    ],
    "METHODS": [
        "Item 5: Eligibility criteria and study characteristics",
        "Item 6: Information sources and search dates",
        "Item 7: Full electronic search strategy for at least one database",
        "Item 8: Selection process and screening procedures",
        "Item 9: Data collection process and extraction tools",
        "Item 10: List and definition of all outcomes and variables",
        "Item 11: Risk of bias / quality assessment methodology",
        "Item 12: Effect measures and metrics",
        "Item 13: Synthesis methods and narrative integration"
    ],
    "RESULTS": [
        "Item 16: Study selection flow diagram and inclusion metrics",
        "Item 17: Study characteristics table",
        "Item 18: Risk of bias in included studies",
        "Item 19: Results of individual studies",
        "Item 20: Results of syntheses and narrative analysis"
    ],
    "DISCUSSION": [
        "Item 23: Discussion of evidence in context of limitations"
    ],
    "OTHER": [
        "Item 24: Registration and protocol availability",
        "Item 27: Open science, code, and data availability"
    ]
}


def evaluate_prisma_compliance(report_text: str, counts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates whether the generated systematic review adheres to PRISMA 2020 sections.
    """
    checklist_status = {}
    report_lower = report_text.lower() if report_text else ""

    rules = {
        "Item 1: Title": "systematic review" in report_lower or "literature review" in report_lower,
        "Item 2: Structured Abstract": "abstract" in report_lower,
        "Item 3 & 4: Rationale & Objectives": "introduction" in report_lower or "background" in report_lower or "rationale" in report_lower,
        "Item 5: Eligibility Criteria": "eligibility" in report_lower or "inclusion criteria" in report_lower,
        "Item 6 & 7: Information Sources & Search Strategy": "search strategy" in report_lower or "pubmed" in report_lower or "arxiv" in report_lower,
        "Item 8: Selection Process": "screening" in report_lower or "selection process" in report_lower,
        "Item 9 & 10: Data Extraction & Variables": "data extraction" in report_lower or "variables" in report_lower,
        "Item 11: Risk of Bias Assessment": "risk of bias" in report_lower or "quality assessment" in report_lower or "appraisal" in report_lower,
        "Item 13: Synthesis Methods": "synthesis" in report_lower or "thematic analysis" in report_lower,
        "Item 16: Study Selection (PRISMA Flow)": counts.get("total_identified", 0) > 0,
        "Item 17: Study Characteristics": "study characteristics" in report_lower or "evidence table" in report_lower,
        "Item 20: Synthesis Results": "findings" in report_lower or "results" in report_lower,
        "Item 23: Discussion & Limitations": "discussion" in report_lower or "limitations" in report_lower,
        "Item 27: Data & Code Availability": "code" in report_lower or "reproducibility" in report_lower or "github" in report_lower
    }

    satisfied = sum(1 for v in rules.values() if v)
    total = len(rules)
    compliance_score = round((satisfied / total) * 100, 1)

    return {
        "score_percentage": compliance_score,
        "satisfied_items": satisfied,
        "total_items": total,
        "checklist_details": rules,
        "status": "COMPLIANT" if compliance_score >= 80 else "PARTIALLY_COMPLIANT"
    }
