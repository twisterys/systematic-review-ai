"""
State definition for the Systematic Review Multi-Agent Pipeline.
Follows PRISMA 2020 standards and enables full transparency and auditability.
Uses standard library TypedDict / dataclasses for zero-dependency reliability.
"""

from typing import List, Dict, Any, Optional, TypedDict
from dataclasses import dataclass, field


@dataclass
class StudyRecord:
    id: str
    source: str  # PubMed, arXiv, SemanticScholar, OpenAlex
    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[str] = None
    abstract: str = ""
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    full_text: Optional[str] = None
    
    # Screening metadata
    screened_title_abstract: bool = False
    include_title_abstract: Optional[bool] = None
    reason_title_abstract: str = ""
    
    screened_full_text: bool = False
    include_full_text: Optional[bool] = None
    reason_full_text: str = ""
    
    # Data extraction & Quality appraisal
    extracted_data: Optional[Dict[str, Any]] = None
    risk_of_bias: Optional[Dict[str, Any]] = None


@dataclass
class ProtocolDefinition:
    population_or_context: str = ""
    intervention_or_concept: str = ""
    comparison: str = ""
    outcomes: str = ""
    study_designs: List[str] = field(default_factory=list)
    inclusion_criteria: List[str] = field(default_factory=list)
    exclusion_criteria: List[str] = field(default_factory=list)
    search_keywords: List[str] = field(default_factory=list)


@dataclass
class PrismaCounts:
    database_results: Dict[str, int] = field(default_factory=dict)
    total_identified: int = 0
    duplicates_removed: int = 0
    records_screened_ta: int = 0
    records_excluded_ta: int = 0
    reports_sought_fulltext: int = 0
    reports_not_retrieved: int = 0
    reports_assessed_fulltext: int = 0
    reports_excluded_fulltext: int = 0
    studies_included: int = 0


class SystematicReviewState(TypedDict):
    # Inputs
    research_topic: str
    research_question: str
    
    # Protocol & Planning
    protocol: Dict[str, Any]
    search_strategies: Dict[str, str]  # {source: boolean_query}
    
    # Retrieval & Dedup
    raw_studies: List[Dict[str, Any]]
    deduplicated_studies: List[Dict[str, Any]]
    
    # Screening
    ta_screened_studies: List[Dict[str, Any]]
    fulltext_screened_studies: List[Dict[str, Any]]
    included_studies: List[Dict[str, Any]]
    
    # Extraction & Appraisal
    extracted_evidence: List[Dict[str, Any]]
    quality_assessments: List[Dict[str, Any]]
    
    # Synthesis & Outputs
    narrative_synthesis: str
    prisma_counts: Dict[str, Any]
    prisma_checklist_report: Dict[str, Any]
    final_report_markdown: str
    
    # Quality Assurance / Control Loop
    critic_verdict: str  # "APPROVED" or "REVISE"
    critic_feedback: str
    revision_iteration: int
    
    # Execution & Audit Trail
    audit_trail: List[Dict[str, Any]]
    status_message: str
