"""
Search Strategy Agent.
Formulates optimized Boolean and database-specific search strings for PubMed, arXiv,
Semantic Scholar, and OpenAlex.
"""

from typing import Dict, Any
from ..config import get_llm
import json
import re


SEARCH_STRATEGY_SYSTEM_PROMPT = """You are an Academic Information Specialist / Medical & Scientific Librarian.
Given a systematic review protocol (PICO and keywords), design customized query strings for:
1. pubmed: Boolean syntax with MeSH terms and title/abstract tags [tiab].
2. arxiv: Clean Boolean syntax suited for arXiv Atom API (AND, OR, ti/abs).
3. semantic_scholar: Focused keyword phrase string for semantic search.
4. openalex: High-recall phrase query.

Return STRICT JSON matching:
{
  "pubmed": "query string",
  "arxiv": "query string",
  "semantic_scholar": "query string",
  "openalex": "query string"
}
Only output valid JSON.
"""


def run_search_strategy_agent(protocol: Dict[str, Any], topic: str) -> Dict[str, str]:
    """
    Executes the Search Strategy Agent to craft database-specific query strings.
    """
    llm = get_llm(temperature=0.1)
    prompt = f"Topic: {topic}\nProtocol: {json.dumps(protocol, indent=2)}"

    if llm:
        try:
            if hasattr(llm, "invoke"):
                res = llm.invoke(f"{SEARCH_STRATEGY_SYSTEM_PROMPT}\n\n{prompt}")
                content = res.content if hasattr(res, "content") else str(res)
            else:
                res = llm.generate_content(f"{SEARCH_STRATEGY_SYSTEM_PROMPT}\n\n{prompt}")
                content = res.text

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"[Search Strategy Agent] LLM Error: {e}")

    # Robust default query generator
    clean_topic = re.sub(r"[^\w\s]", " ", topic)
    words = [w for w in clean_topic.split() if len(w) > 3]
    top_words = " AND ".join(words[:4]) if words else "multi agent systems"

    return {
        "pubmed": f"({topic}[tiab]) OR (multi-agent[tiab] AND {words[0] if words else 'talent'}[tiab])",
        "arxiv": f"all:{top_words}",
        "semantic_scholar": topic,
        "openalex": topic
    }
