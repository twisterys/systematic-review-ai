"""
Deduplication utility for multi-source academic literature.
Performs exact matching on DOI and fuzzy string matching on normalized titles.
"""

import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher


def normalize_title(title: str) -> str:
    """Normalize paper title for fuzzy comparison."""
    if not title:
        return ""
    # Lowercase, remove punctuation and extra whitespaces
    clean = title.lower()
    clean = re.sub(r"[^\w\s]", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def is_title_duplicate(title_a: str, title_b: str, threshold: float = 0.90) -> bool:
    """Check if two titles are near duplicates using sequence matching."""
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True
    ratio = SequenceMatcher(None, norm_a, norm_b).ratio()
    return ratio >= threshold


def deduplicate_studies(studies: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Deduplicates a list of study records based on:
    1. Exact DOI match (if DOI is present)
    2. Fuzzy match on normalized title (threshold = 0.90)

    Returns:
        (deduplicated_list, count_of_duplicates_removed)
    """
    seen_dois = set()
    deduped = []
    duplicates_count = 0

    for study in studies:
        doi = (study.get("doi") or "").strip().lower()
        title = study.get("title", "")
        
        # 1. Check DOI
        if doi and doi in seen_dois:
            duplicates_count += 1
            continue

        # 2. Check Fuzzy Title against already retained studies
        is_dup = False
        for kept in deduped:
            if is_title_duplicate(title, kept.get("title", "")):
                is_dup = True
                break

        if is_dup:
            duplicates_count += 1
            continue

        if doi:
            seen_dois.add(doi)
        deduped.append(study)

    return deduped, duplicates_count
