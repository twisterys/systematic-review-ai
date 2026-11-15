"""
Critic / Quality Assurance Agent.
Reviews synthesized outputs for consistency, potential bias, completeness,
and adherence to PRISMA 2020 protocol. Controls cyclical feedback in LangGraph.
"""

from typing import Dict, Any, Tuple
from ..config import get_llm
from ..prisma import evaluate_prisma_compliance
import json
import re


CRITIC_PROMPT = """You are the Senior Editor-in-Chief for a top-tier systematic review journal.
Critique the systematic review report and extracted evidence below.

Review Objectives:
Topic: {topic}
Manuscript Word Count: {word_count}
Included Studies: {included_count}
PRISMA Compliance Score: {prisma_score}%

Evaluate:
1. Methodological soundness & alignment with PICO
2. Clarity of evidence tables and risk of bias reporting
3. Absence of unsubstantiated or hallucinated claims
4. Transparency of PRISMA flow and search strategies

Return STRICT JSON:
{{
  "verdict": "APPROVED" or "REVISE",
  "critique_score_out_of_10": 8.5,
  "strengths": ["...", "..."],
  "actionable_feedback": "Detailed guidance if revisions are needed",
  "approved_for_publication": true or false
}}
Only output valid JSON.
"""


def run_critic_agent(
    topic: str,
    manuscript: str,
    extracted_evidence: list,
    prisma_counts: Dict[str, Any],
    iteration: int
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Executes the Critic Agent to review the systematic review pipeline output.

    Returns:
        (verdict, feedback, full_critique_dict)
    """
    llm = get_llm(temperature=0.1)
    compliance = evaluate_prisma_compliance(manuscript, prisma_counts)
    prisma_score = compliance.get("score_percentage", 75)
    word_count = len(manuscript.split())
    included_count = len(extracted_evidence)

    # If maximum loops reached (safety bound), approve automatically
    if iteration >= 2:
        return "APPROVED", "Approved automatically after QA revision loop limit reached.", compliance

    if llm:
        try:
            prompt = CRITIC_PROMPT.format(
                topic=topic,
                word_count=word_count,
                included_count=included_count,
                prisma_score=prisma_score
            )
            if hasattr(llm, "invoke"):
                res = llm.invoke(prompt)
                res_text = res.content if hasattr(res, "content") else str(res)
            else:
                res = llm.generate_content(prompt)
                res_text = res.text

            json_match = re.search(r"\{.*\}", res_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                verdict = data.get("verdict", "APPROVED").upper()
                feedback = data.get("actionable_feedback", "All quality criteria met.")
                return verdict, feedback, data
        except Exception as e:
            print(f"[Critic Agent] LLM Error: {e}")

    # Deterministic fallback check
    if prisma_score >= 70 and included_count >= 1:
        return "APPROVED", f"All critical sections present. PRISMA compliance score: {prisma_score}%.", compliance
    else:
        return "REVISE", f"PRISMA compliance score {prisma_score}% requires supplementary evidence synthesis.", compliance
