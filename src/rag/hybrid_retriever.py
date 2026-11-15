"""
Hybrid retriever combining dense retrieval with keyword matching and re-ranking.
"""

from typing import List, Dict, Any
from .vector_store import PaperVectorStore


class HybridRetriever:
    def __init__(self, vector_store: PaperVectorStore):
        self.vector_store = vector_store

    def retrieve_grounding_evidence(self, query: str, top_k: int = 5) -> str:
        """
        Retrieves top relevant evidence snippets formatted for LLM grounding.
        """
        hits = self.vector_store.search(query, top_k=top_k)
        if not hits:
            return "No specific vector store documents indexed."

        snippets = []
        for i, hit in enumerate(hits, 1):
            meta = hit.get("metadata", {})
            title = meta.get("title", "Untitled")
            year = meta.get("year", "")
            source = meta.get("source", "")
            doc = hit.get("document", "")
            
            snippets.append(
                f"[Evidence #{i}] {title} ({year}) [{source}]:\n{doc[:800]}..."
            )
        return "\n\n".join(snippets)
