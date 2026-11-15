"""
Configuration manager for LLM, vector store, and search API credentials.
Supports Google Gemini, OpenAI, and local mock fallbacks.
"""

import os
from typing import Optional

# Optional dotenv loader
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Minimal custom .env parser
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception:
            pass


class Settings:
    # LLM Settings
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Academic APIs
    NCBI_API_KEY: Optional[str] = os.getenv("NCBI_API_KEY")
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    OPENALEX_EMAIL: Optional[str] = os.getenv("OPENALEX_EMAIL", "researcher@example.com")
    
    # Output and Vector Store
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./output/chroma_db")


def get_llm(temperature: float = 0.2):
    """
    Returns an instantiated LangChain Chat model (Gemini or OpenAI).
    If no API key is provided, returns None or a Mock LLM for local dry-runs.
    """
    provider = Settings.DEFAULT_PROVIDER

    if provider == "gemini" and Settings.GEMINI_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=Settings.GEMINI_MODEL,
                google_api_key=Settings.GEMINI_API_KEY,
                temperature=temperature
            )
        except Exception:
            pass

        try:
            import google.generativeai as genai
            genai.configure(api_key=Settings.GEMINI_API_KEY)
            return genai.GenerativeModel(Settings.GEMINI_MODEL)
        except Exception:
            pass

    if (provider == "openai" or not Settings.GEMINI_API_KEY) and Settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=Settings.OPENAI_MODEL,
                api_key=Settings.OPENAI_API_KEY,
                temperature=temperature
            )
        except Exception:
            pass

    return None
