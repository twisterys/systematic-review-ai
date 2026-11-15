"""
Zero-dependency HTTP client wrapper using urllib with requests compatibility.
Ensures tools run even before external pip dependencies are installed.
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional


class SimpleResponse:
    def __init__(self, content: bytes, status_code: int):
        self.content = content
        self.status_code = status_code
        self.text = content.decode("utf-8", errors="replace")

    def json(self) -> Dict[str, Any]:
        return json.loads(self.text)


def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> SimpleResponse:
    """Performs HTTP GET with urllib.request fallback."""
    # Try requests first if available
    try:
        import requests
        resp = requests.get(url, headers=headers, timeout=timeout)
        return SimpleResponse(resp.content, resp.status_code)
    except ImportError:
        pass

    # Urllib fallback
    req_headers = {"User-Agent": "SystematicReviewAgent/1.0 (academic-research)"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            return SimpleResponse(content, response.status)
    except urllib.error.HTTPError as e:
        return SimpleResponse(e.read(), e.code)
    except Exception as e:
        print(f"[HTTP Request Error] {url}: {e}")
        return SimpleResponse(b"", 500)
