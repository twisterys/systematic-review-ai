"""
PDF Parser and Full-Text Retrieval Tool.
Extracts text from open-access PDF URLs or local PDF files.
"""

import io
from typing import Optional
from ..utils import http_get


def extract_text_from_pdf_url(pdf_url: str, timeout: int = 15) -> Optional[str]:
    """Downloads and extracts text from an open-access PDF URL."""
    if not pdf_url:
        return None
    try:
        resp = http_get(pdf_url, timeout=timeout)
        if resp.status_code != 200 or not resp.content:
            return None

        # Try pypdf if installed
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(resp.content))
            pages_text = []
            for page in reader.pages[:15]:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            full_text = "\n\n".join(pages_text).strip()
            return full_text if len(full_text) > 100 else None
        except Exception:
            return None
    except Exception as e:
        print(f"[PDF Parser] Failed to retrieve {pdf_url}: {e}")
        return None
