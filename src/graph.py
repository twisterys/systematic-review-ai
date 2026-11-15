"""
LangGraph Multi-Agent Orchestration Workflow.
Coordinates state transitions, cyclic critique loops, and checkpointing.
"""

from typing import Dict, Any, Callable, Optional
from .state import SystematicReviewState
from .rag import PaperVectorStore
from .prisma import compute_prisma_flow_counts, evaluate_prisma_compliance
from .agents import (
    run_coordinator_agent,
    run_search_strategy_agent,
    run_retrieval_agent,
    run_title_abstract_screening,
    run_full_text_screening,
    run_extraction_and_appraisal,
    run_synthesis_and_writing_agent,
    run_critic_agent
)


class SystematicReviewPipeline:
    """
    Orchestrator for the multi-agent systematic review graph.
    Supports step-by-step UI callback notifications for interactive Streamlit execution.
    """

    def __init__(self, vector_store: Optional[PaperVectorStore] = None):
        self.vector_store = vector_store or PaperVectorStore()

    def coordinator_step(self, state: SystematicReviewState) -> SystematicReviewState:
        topic = state.get("research_topic", "")
        question = state.get("research_question", "")
        protocol = run_coordinator_agent(topic, question)
        state["protocol"] = protocol
        state["status_message"] = "Protocol established with PICO criteria."
        state.setdefault("audit_trail", []).append({
            "stage": "Coordinator",
            "action": "Generated PICO protocol and inclusion/exclusion criteria."
        })
        return state

    def search_strategy_step(self, state: SystematicReviewState) -> SystematicReviewState:
        protocol = state.get("protocol", {})
        topic = state.get("research_topic", "")
        strategies = run_search_strategy_agent(protocol, topic)
        state["search_strategies"] = strategies
        state["status_message"] = "Search strategies generated for PubMed, arXiv, Semantic Scholar, and OpenAlex."
        state["audit_trail"].append({
            "stage": "Search Strategy",
            "action": f"Formulated Boolean queries across 4 databases: {list(strategies.keys())}"
        })
        return state

    def retrieval_step(self, state: SystematicReviewState, max_per_source: int = 15) -> SystematicReviewState:
        strategies = state.get("search_strategies", {})
        raw, deduped, dups_removed = run_retrieval_agent(
            strategies, self.vector_store, max_per_source=max_per_source
        )
        state["raw_studies"] = raw
        state["deduplicated_studies"] = deduped
        state["status_message"] = f"Retrieved {len(raw)} records across databases; {dups_removed} duplicates removed."
        state["audit_trail"].append({
            "stage": "Retrieval & Dedup",
            "action": f"Pooled {len(raw)} studies -> Deduplicated to {len(deduped)} unique records."
        })
        return state

    def screening_ta_step(self, state: SystematicReviewState) -> SystematicReviewState:
        deduped = state.get("deduplicated_studies", [])
        protocol = state.get("protocol", {})
        topic = state.get("research_topic", "")
        screened = run_title_abstract_screening(deduped, protocol, topic)
        state["ta_screened_studies"] = screened
        passed = sum(1 for s in screened if s.get("include_title_abstract"))
        state["status_message"] = f"Title/Abstract screening: {passed}/{len(screened)} studies eligible."
        state["audit_trail"].append({
            "stage": "Title/Abstract Screening",
            "action": f"Screened {len(screened)} records -> {passed} retained for full-text assessment."
        })
        return state

    def screening_fulltext_step(self, state: SystematicReviewState) -> SystematicReviewState:
        ta_screened = state.get("ta_screened_studies", [])
        protocol = state.get("protocol", {})
        eligible_ta = [s for s in ta_screened if s.get("include_title_abstract")]
        assessed, final_included = run_full_text_screening(eligible_ta, protocol)
        state["fulltext_screened_studies"] = assessed
        state["included_studies"] = final_included
        state["status_message"] = f"Full-text screening: {len(final_included)}/{len(assessed)} studies met all criteria."
        state["audit_trail"].append({
            "stage": "Full-Text Screening",
            "action": f"Assessed {len(assessed)} reports -> {len(final_included)} definitively included."
        })
        return state

    def extraction_step(self, state: SystematicReviewState) -> SystematicReviewState:
        included = state.get("included_studies", [])
        evidence, quality = run_extraction_and_appraisal(included)
        state["extracted_evidence"] = evidence
        state["quality_assessments"] = quality
        state["status_message"] = f"Extracted structured evidence and appraised Risk of Bias for {len(included)} studies."
        state["audit_trail"].append({
            "stage": "Extraction & Appraisal",
            "action": f"Generated evidence tables and risk-of-bias ratings for {len(included)} studies."
        })
        return state

    def synthesis_step(self, state: SystematicReviewState) -> SystematicReviewState:
        topic = state.get("research_topic", "")
        question = state.get("research_question", "")
        protocol = state.get("protocol", {})
        strategies = state.get("search_strategies", {})
        evidence = state.get("extracted_evidence", [])
        quality = state.get("quality_assessments", [])
        
        counts = compute_prisma_flow_counts(state)
        state["prisma_counts"] = counts
        
        narrative, manuscript = run_synthesis_and_writing_agent(
            topic, question, protocol, strategies, evidence, quality, counts
        )
        state["narrative_synthesis"] = narrative
        state["final_report_markdown"] = manuscript
        
        compliance = evaluate_prisma_compliance(manuscript, counts)
        state["prisma_checklist_report"] = compliance
        
        state["status_message"] = "PRISMA manuscript and narrative synthesis synthesized."
        state["audit_trail"].append({
            "stage": "Synthesis & Writing",
            "action": "Generated final manuscript with evidence tables and PRISMA 2020 flow diagram."
        })
        return state

    def critic_step(self, state: SystematicReviewState) -> SystematicReviewState:
        topic = state.get("research_topic", "")
        manuscript = state.get("final_report_markdown", "")
        evidence = state.get("extracted_evidence", [])
        counts = state.get("prisma_counts", {})
        iteration = state.get("revision_iteration", 0)

        verdict, feedback, critique_data = run_critic_agent(
            topic, manuscript, evidence, counts, iteration
        )
        state["critic_verdict"] = verdict
        state["critic_feedback"] = feedback
        state["revision_iteration"] = iteration + 1
        state["status_message"] = f"Critic Agent QA: Verdict = {verdict}. {feedback}"
        state["audit_trail"].append({
            "stage": "Critic & QA",
            "action": f"Quality verdict: {verdict}. Feedback: {feedback}"
        })
        return state

    def run_full_pipeline(
        self,
        topic: str,
        question: str,
        callback: Optional[Callable[[str, int, SystematicReviewState], None]] = None
    ) -> SystematicReviewState:
        """
        Executes the entire multi-agent systematic review pipeline end-to-end.
        """
        state: SystematicReviewState = {
            "research_topic": topic,
            "research_question": question,
            "protocol": {},
            "search_strategies": {},
            "raw_studies": [],
            "deduplicated_studies": [],
            "ta_screened_studies": [],
            "fulltext_screened_studies": [],
            "included_studies": [],
            "extracted_evidence": [],
            "quality_assessments": [],
            "narrative_synthesis": "",
            "prisma_counts": {},
            "prisma_checklist_report": {},
            "final_report_markdown": "",
            "critic_verdict": "PENDING",
            "critic_feedback": "",
            "revision_iteration": 0,
            "audit_trail": [],
            "status_message": "Initializing pipeline..."
        }

        stages = [
            ("🧠 Establishing Protocol (Coordinator Agent)", self.coordinator_step),
            ("🔍 Designing Search Queries (Search Strategy Agent)", self.search_strategy_step),
            ("📥 Querying Academic Databases (Retrieval Agent)", self.retrieval_step),
            ("📋 Title & Abstract Screening (Screening Agent 1)", self.screening_ta_step),
            ("📄 Full-Text Eligibility Appraisal (Screening Agent 2)", self.screening_fulltext_step),
            ("📊 Data Extraction & Quality Appraisal (Extraction Agent)", self.extraction_step),
            ("✍️ Synthesizing PRISMA Report (Synthesis Agent)", self.synthesis_step),
            ("🔎 Quality Assurance Review (Critic Agent)", self.critic_step),
        ]

        total_steps = len(stages)
        for i, (desc, step_fn) in enumerate(stages, 1):
            if callback:
                callback(desc, int((i / total_steps) * 100), state)
            state = step_fn(state)

        # Check cyclic loop condition from Critic
        if state.get("critic_verdict") == "REVISE" and state.get("revision_iteration", 0) < 2:
            if callback:
                callback("🔄 Executing Critic-guided Revision Loop...", 90, state)
            state = self.synthesis_step(state)
            state = self.critic_step(state)

        if callback:
            callback("🏁 Systematic Review Completed Successfully!", 100, state)

        return state


def build_langgraph_workflow():
    """
    Compiles a native LangGraph StateGraph instance for stateful workflows.
    """
    try:
        from langgraph.graph import StateGraph, END
        from .state import SystematicReviewState

        pipeline = SystematicReviewPipeline()
        workflow = StateGraph(SystematicReviewState)

        workflow.add_node("coordinator", pipeline.coordinator_step)
        workflow.add_node("search_strategy", pipeline.search_strategy_step)
        workflow.add_node("retrieval", pipeline.retrieval_step)
        workflow.add_node("screening_ta", pipeline.screening_ta_step)
        workflow.add_node("screening_fulltext", pipeline.screening_fulltext_step)
        workflow.add_node("extraction", pipeline.extraction_step)
        workflow.add_node("synthesis", pipeline.synthesis_step)
        workflow.add_node("critic", pipeline.critic_step)

        workflow.set_entry_point("coordinator")
        workflow.add_edge("coordinator", "search_strategy")
        workflow.add_edge("search_strategy", "retrieval")
        workflow.add_edge("retrieval", "screening_ta")
        workflow.add_edge("screening_ta", "screening_fulltext")
        workflow.add_edge("screening_fulltext", "extraction")
        workflow.add_edge("extraction", "synthesis")
        workflow.add_edge("synthesis", "critic")

        def route_critic(state: SystematicReviewState) -> str:
            if state.get("critic_verdict") == "REVISE" and state.get("revision_iteration", 0) < 2:
                return "synthesis"
            return END

        workflow.add_conditional_edges(
            "critic",
            route_critic,
            {
                "synthesis": "synthesis",
                END: END
            }
        )

        return workflow.compile()
    except Exception as e:
        print(f"[LangGraph] Notice: Native LangGraph compile skipped ({e}), using runtime pipeline.")
        return None
