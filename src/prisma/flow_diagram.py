"""
PRISMA 2020 Flow Diagram Generator.
Tracks identification, deduplication, title/abstract screening,
full-text retrieval & eligibility, and final included studies.
"""

from typing import Dict, Any


def compute_prisma_flow_counts(state: Dict[str, Any]) -> Dict[str, int]:
    """Computes exact counts for the PRISMA 2020 flow diagram from pipeline state."""
    raw_studies = state.get("raw_studies", [])
    deduped = state.get("deduplicated_studies", [])
    ta_screened = state.get("ta_screened_studies", [])
    ft_screened = state.get("fulltext_screened_studies", [])
    included = state.get("included_studies", [])

    # Database Breakdown
    db_counts = {}
    for s in raw_studies:
        source = s.get("source", "Other")
        db_counts[source] = db_counts.get(source, 0) + 1

    total_identified = len(raw_studies)
    total_deduped = len(deduped)
    duplicates_removed = total_identified - total_deduped

    # Title / Abstract screening counts
    records_screened_ta = len(ta_screened)
    ta_excluded = sum(1 for s in ta_screened if s.get("include_title_abstract") is False)

    # Full text sought
    reports_sought = sum(1 for s in ta_screened if s.get("include_title_abstract") is True)
    reports_assessed_ft = len(ft_screened)
    reports_not_retrieved = max(0, reports_sought - reports_assessed_ft)
    
    ft_excluded = sum(1 for s in ft_screened if s.get("include_full_text") is False)
    final_included = len(included)

    return {
        "db_counts": db_counts,
        "total_identified": total_identified,
        "duplicates_removed": duplicates_removed,
        "records_screened_ta": records_screened_ta,
        "records_excluded_ta": ta_excluded,
        "reports_sought": reports_sought,
        "reports_not_retrieved": reports_not_retrieved,
        "reports_assessed_ft": reports_assessed_ft,
        "reports_excluded_ft": ft_excluded,
        "final_included": final_included
    }


def generate_mermaid_flow_diagram(counts: Dict[str, Any]) -> str:
    """Generates Mermaid flowchart representing the PRISMA 2020 Flow Diagram."""
    db_breakdown = ", ".join([f"{k}: {v}" for k, v in counts.get("db_counts", {}).items()]) or "Databases"
    total_id = counts.get("total_identified", 0)
    dup_rem = counts.get("duplicates_removed", 0)
    screened_ta = counts.get("records_screened_ta", 0)
    excl_ta = counts.get("records_excluded_ta", 0)
    sought = counts.get("reports_sought", 0)
    not_ret = counts.get("reports_not_retrieved", 0)
    assessed_ft = counts.get("reports_assessed_ft", 0)
    excl_ft = counts.get("reports_excluded_ft", 0)
    final_inc = counts.get("final_included", 0)

    diagram = f"""flowchart TD
    subgraph IDENTIFICATION ["Identification of studies via databases"]
        A["Records identified from:\\n{db_breakdown}\\n(Total n = {total_id})"]
        B["Records removed before screening:\\nDuplicate records removed (n = {dup_rem})"]
        A --> B
    end

    subgraph SCREENING ["Screening"]
        C["Records screened (Title & Abstract)\\n(n = {screened_ta})"]
        D["Records excluded by Title/Abstract\\n(n = {excl_ta})"]
        B --> C
        C --> D
        C --> E["Reports sought for retrieval\\n(n = {sought})"]
        F["Reports not retrieved\\n(n = {not_ret})"]
        E --> F
        E --> G["Reports assessed for eligibility (Full-text)\\n(n = {assessed_ft})"]
        H["Reports excluded (Full-text criteria)\\n(n = {excl_ft})"]
        G --> H
    end

    subgraph INCLUDED ["Included"]
        I["Studies included in review\\n(n = {final_inc})"]
        G --> I
    end
"""
    return diagram
