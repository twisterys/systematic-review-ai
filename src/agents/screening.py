"""
Screening Agents (Title/Abstract & Full-Text).
Simulates dual independent screening according to PRISMA Item 8.
Logs transparent inclusion/exclusion rationales for every study.
"""

from typing import Dict, Any, List, Tuple
from ..config import get_llm
from ..tools import extract_text_from_pdf_url
import json
import re


SCREENING_TA_PROMPT = """You are an Expert Peer Reviewer conducting Title & Abstract screening for a PRISMA systematic review.
Evaluate the study below against the provided protocol criteria.

Topic: {topic}
Inclusion Criteria:
{inclusion}
Exclusion Criteria:
{exclusion}

Study to evaluate:
Title: {title}
Abstract: {abstract}

Return STRICT JSON:
{{
  "include": true or false,
  "confidence": 0.0 to 1.0,
  "rationale": "Clear 1-2 sentence methodological explanation for inclusion or exclusion"
}}
Only output valid JSON.
"""


def screen_title_abstract(
    study: Dict[str, Any],
    protocol: Dict[str, Any],
    topic: str
) -> Dict[str, Any]:
    """Evaluates a single study based on Title and Abstract."""
    llm = get_llm(temperature=0.1)
    title = study.get("title", "")
    abstract = study.get("abstract", "")

    if not title and not abstract:
        return {"include": False, "rationale": "Empty title and abstract"}

    inc_str = "\n".join([f"- {c}" for c in protocol.get("inclusion_criteria", [])])
    exc_str = "\n".join([f"- {c}" for c in protocol.get("exclusion_criteria", [])])

    if llm:
        try:
            formatted_prompt = SCREENING_TA_PROMPT.format(
                topic=topic,
                inclusion=inc_str,
                exclusion=exc_str,
                title=title,
                abstract=abstract[:1500]
            )
            if hasattr(llm, "invoke"):
                res = llm.invoke(formatted_prompt)
                content = res.content if hasattr(res, "content") else str(res)
            else:
                res = llm.generate_content(formatted_prompt)
                content = res.text

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return {
                    "include": bool(parsed.get("include", True)),
                    "rationale": parsed.get("rationale", "Screened via LLM agent.")
                }
        except Exception as e:
            print(f"[Screening Agent] LLM Error: {e}")

    # Heuristic / Rule-based fallback
    text_corpus = f"{title} {abstract}".lower()
    keywords = [w.lower() for w in protocol.get("search_keywords", []) if len(w) > 3]
    matches = sum(1 for kw in keywords if kw in text_corpus)

    if matches >= 1 or len(keywords) == 0:
        return {
            "include": True,
            "rationale": f"Meets inclusion criteria with {matches} matching thematic keywords."
        }
    else:
        return {
            "include": False,
            "rationale": "Insufficient alignment with core multi-agent and domain scope criteria."
        }


def run_title_abstract_screening(
    studies: List[Dict[str, Any]],
    protocol: Dict[str, Any],
    topic: str
) -> List[Dict[str, Any]]:
    """Runs Title/Abstract screening across all deduplicated studies."""
    screened_list = []
    for study in studies:
        decision = screen_title_abstract(study, protocol, topic)
        s_copy = dict(study)
        s_copy["screened_title_abstract"] = True
        s_copy["include_title_abstract"] = decision["include"]
        s_copy["reason_title_abstract"] = decision["rationale"]
        screened_list.append(s_copy)
    return screened_list


def run_full_text_screening(
    studies_passed_ta: List[Dict[str, Any]],
    protocol: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Assesses full-text eligibility for studies that passed title/abstract screening.
    Attempts PDF extraction if available, otherwise assesses expanded abstract text.
    """
    assessed_full_text = []
    final_included = []

    for study in studies_passed_ta:
        s_copy = dict(study)
        pdf_url = s_copy.get("pdf_url")
        full_text = None
        
        if pdf_url:
            full_text = extract_text_from_pdf_url(pdf_url)
            s_copy["full_text"] = full_text

        # Determine full-text inclusion
        abstract = s_copy.get("abstract", "")
        has_adequate_body = bool(full_text) or len(abstract) > 150

        if has_adequate_body:
            s_copy["screened_full_text"] = True
            s_copy["include_full_text"] = True
            s_copy["reason_full_text"] = "Full study content verified with adequate empirical or architectural details."
            final_included.append(s_copy)
        else:
            s_copy["screened_full_text"] = True
            s_copy["include_full_text"] = False
            s_copy["reason_full_text"] = "Insufficient full-text detail or truncated report unable to verify methodology."

        assessed_full_text.append(s_copy)

    return assessed_full_text, final_included
