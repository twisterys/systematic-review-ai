"""
Coordinator / Planner Agent.
Decomposes the research question into PICO framework, establishes review protocol,
and specifies explicit inclusion and exclusion criteria.
"""

from typing import Dict, Any
from ..config import get_llm
import json
import re


COORDINATOR_SYSTEM_PROMPT = """You are a Principal Systematic Review Methodologist adhering strictly to PRISMA 2020 guidelines.
Your task is to take a research topic or research question and design a formal Systematic Literature Review Protocol.

You must decompose the topic using the PICO framework:
- Population / Context: The target domain, entities, or systems.
- Intervention / Concept: The primary technology, agentic AI architecture, or methodology being evaluated.
- Comparison: Alternative architectures, baseline models, human reviewers, or traditional approaches (if applicable).
- Outcomes: Key metrics, performance, transparency, autonomy, effectiveness, or impact measures.

Define strict, unambiguous:
- inclusion_criteria: List of 3-5 conditions that studies MUST satisfy.
- exclusion_criteria: List of 3-5 conditions that will disqualify a study.
- search_keywords: High-value keywords and domain synonyms.

Return your response as STRICT JSON matching this schema:
{
  "population_or_context": "...",
  "intervention_or_concept": "...",
  "comparison": "...",
  "outcomes": "...",
  "inclusion_criteria": ["...", "..."],
  "exclusion_criteria": ["...", "..."],
  "search_keywords": ["...", "..."]
}
Only output valid JSON.
"""


def run_coordinator_agent(research_topic: str, research_question: str) -> Dict[str, Any]:
    """
    Executes the Coordinator Agent to generate a systematic review protocol.
    """
    llm = get_llm(temperature=0.1)
    prompt = f"Topic: {research_topic}\nResearch Question: {research_question}"

    if llm:
        try:
            # LangChain or Gemini call
            if hasattr(llm, "invoke"):
                res = llm.invoke(f"{COORDINATOR_SYSTEM_PROMPT}\n\n{prompt}")
                content = res.content if hasattr(res, "content") else str(res)
            else:
                # Raw Gemini model
                res = llm.generate_content(f"{COORDINATOR_SYSTEM_PROMPT}\n\n{prompt}")
                content = res.text

            # Parse JSON safely
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"[Coordinator Agent] LLM Error: {e}")

    # Deterministic Academic Fallback
    keywords = [w for w in re.split(r"\W+", research_topic.lower()) if len(w) > 3]
    return {
        "population_or_context": f"Academic literature, autonomous systems, and platforms in: {research_topic}",
        "intervention_or_concept": "Agentic AI workflows, multi-agent coordination, and automated reasoning pipelines",
        "comparison": "Single-agent architectures, manual human processes, and non-agentic baselines",
        "outcomes": "Autonomy, rigor, accuracy, execution transparency, and reproducibility",
        "inclusion_criteria": [
            f"Studies directly investigating {research_topic} or related multi-agent systems",
            "Peer-reviewed journal articles, conference papers, or preprints with empirical findings or formal architectures",
            "English language publications with available title, abstract, or full text",
            "Studies documenting evaluation metrics, agent roles, or methodological frameworks"
        ],
        "exclusion_criteria": [
            "Non-academic opinion pieces, short slide decks, or marketing press releases",
            "Studies with no direct relevance to agentic AI, cognitive architectures, or systematic evaluation",
            "Duplicate records or articles with missing essential metadata"
        ],
        "search_keywords": keywords + ["multi-agent", "agentic pipeline", "systematic review", "autonomous ecosystem"]
    }
