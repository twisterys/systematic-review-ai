"""
Vector Store wrapper supporting ChromaDB and in-memory fallback.
Provides document chunking and indexing for academic papers.
"""

import os
from typing import List, Dict, Any, Optional

class PaperVectorStore:
    def __init__(self, persist_directory: str = "./output/chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.in_memory_docs: List[Dict[str, Any]] = []
        self._init_backend()

    def _init_backend(self):
        try:
            import chromadb
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name="systematic_review_corpus")
            self.use_chroma = True
        except Exception as e:
            # Fallback to in-memory index
            self.use_chroma = False

    def add_papers(self, papers: List[Dict[str, Any]]):
        """Indexes paper abstracts and available full text chunks."""
        if not papers:
            return

        for p in papers:
            doc_id = p.get("id", "")
            title = p.get("title", "")
            abstract = p.get("abstract", "")
            full_text = p.get("full_text") or ""
            
            combined_text = f"Title: {title}\nAbstract: {abstract}"
            if full_text:
                combined_text += f"\nFull Text Snippet: {full_text[:2000]}"

            meta = {
                "id": doc_id,
                "title": title[:200],
                "year": str(p.get("year", "")),
                "source": p.get("source", ""),
                "doi": p.get("doi", "") or ""
            }

            if self.use_chroma and self.collection:
                try:
                    self.collection.upsert(
                        ids=[doc_id],
                        documents=[combined_text],
                        metadatas=[meta]
                    )
                except Exception:
                    self.in_memory_docs.append({"id": doc_id, "text": combined_text, "meta": meta})
            else:
                self.in_memory_docs.append({"id": doc_id, "text": combined_text, "meta": meta})

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Queries the vector store and returns matching documents."""
        if self.use_chroma and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k, self.collection.count() or 1)
                )
                hits = []
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                for doc, meta in zip(docs, metas):
                    hits.append({"document": doc, "metadata": meta})
                return hits
            except Exception:
                pass

        # In-memory keyword match fallback
        query_words = set(query.lower().split())
        scored = []
        for doc in self.in_memory_docs:
            text_lower = doc["text"].lower()
            score = sum(1 for w in query_words if w in text_lower)
            scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"document": d["text"], "metadata": d["meta"]} for _, d in scored[:top_k]]
