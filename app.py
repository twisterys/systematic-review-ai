"""
Streamlit Web Dashboard for the Systematic Literature Review Multi-Agent Pipeline.
Interactive execution, live agent status, PRISMA flow diagram, evidence tables, and downloads.
"""

import streamlit as st
import time
import os
import json
from src.graph import SystematicReviewPipeline
from src.prisma import generate_mermaid_flow_diagram
from src.evaluation import evaluate_pipeline_run
from src.config import Settings

# Page Configuration
st.set_page_config(
    page_title="Agentic Systematic Review (PRISMA 2020)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic styling
st.markdown("""
<style>
    .report-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Autonomous Multi-Agent Systematic Review Pipeline")
st.caption("PRISMA 2020-Aligned • LangGraph Multi-Agent Orchestration • Hybrid RAG • Transparent Audit Trails")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration & Models")
    
    provider = st.selectbox(
        "LLM Provider",
        ["Google Gemini", "OpenAI GPT-4o"],
        index=0 if Settings.DEFAULT_PROVIDER == "gemini" else 1
    )
    
    if provider == "Google Gemini":
        gemini_key = st.text_input(
            "Gemini API Key",
            value=Settings.GEMINI_API_KEY or "",
            type="password",
            help="Enter your Gemini API key or set GEMINI_API_KEY in .env"
        )
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
            Settings.GEMINI_API_KEY = gemini_key
    else:
        openai_key = st.text_input(
            "OpenAI API Key",
            value=Settings.OPENAI_API_KEY or "",
            type="password"
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
            Settings.OPENAI_API_KEY = openai_key

    st.divider()
    st.subheader("📚 Literature Sources")
    use_pubmed = st.checkbox("PubMed (Entrez)", value=True)
    use_arxiv = st.checkbox("arXiv Preprints", value=True)
    use_s2 = st.checkbox("Semantic Scholar", value=True)
    use_openalex = st.checkbox("OpenAlex", value=True)
    
    max_papers_per_source = st.slider("Max studies per database", min_value=5, max_value=30, value=12)
    
    st.divider()
    st.info("💡 **Demo Topic Preset** available in main view.")

# Main Input Section
default_topic = "Cognitive Multi-Agent Ecosystems for Autonomous Talent Marketplaces"
default_question = "How do decentralized cognitive multi-agent architectures optimize talent matching, bidding, and autonomous negotiation in decentralized talent marketplaces?"

col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    research_topic = st.text_input("🎯 Research Topic:", value=default_topic)
    research_question = st.text_area("❓ Primary Research Question (PICO-guided):", value=default_question, height=75)

with col_in2:
    st.write(" ")
    st.write(" ")
    if st.button("✨ Load Demo Preset", use_container_width=True):
        st.rerun()

start_pipeline = st.button("🚀 Launch Autonomous Systematic Review", type="primary", use_container_width=True)

# Session State for retaining results
if "review_state" not in st.session_state:
    st.session_state.review_state = None
if "eval_metrics" not in st.session_state:
    st.session_state.eval_metrics = None

# Pipeline Execution
if start_pipeline and research_topic:
    progress_bar = st.progress(0)
    status_text = st.empty()
    activity_log = st.empty()
    
    log_messages = []

    def ui_callback(step_desc: str, pct: int, current_state: dict):
        progress_bar.progress(pct)
        status_text.markdown(f"**Current Agent Action:** {step_desc}")
        log_messages.append(f"⏱️ [{pct}%] {step_desc}")
        activity_log.code("\n".join(log_messages[-5:]), language="text")
        time.sleep(0.3)

    t0 = time.time()
    pipeline = SystematicReviewPipeline()
    try:
        with st.spinner("🤖 Multi-agent team executing review according to PRISMA 2020 protocol..."):
            result_state = pipeline.run_full_pipeline(
                topic=research_topic,
                question=research_question,
                callback=ui_callback
            )
        elapsed = time.time() - t0

        st.session_state.review_state = result_state
        st.session_state.eval_metrics = evaluate_pipeline_run(result_state, execution_seconds=elapsed)
        
        progress_bar.progress(100)
        status_text.success(f"✅ Systematic Review completed in {elapsed:.1f} seconds! Review results below.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        progress_bar.progress(0)
        status_text.error(f"❌ {str(e)}")
        st.error(str(e))

# Display Results if available
if st.session_state.review_state:
    state = st.session_state.review_state
    metrics = st.session_state.eval_metrics
    counts = state.get("prisma_counts", {})

    st.divider()
    
    # Top KPI Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Identified Records", counts.get("total_identified", 0))
    m2.metric("Unique Studies", len(state.get("deduplicated_studies", [])))
    m3.metric("Screened Eligible", counts.get("records_screened_ta", 0) - counts.get("records_excluded_ta", 0))
    m4.metric("Included in Review", counts.get("final_included", 0))
    m5.metric("PRISMA Compliance", f"{state.get('prisma_checklist_report', {}).get('score_percentage', 85)}%")

    # Tabs View
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 PRISMA Manuscript",
        "📊 PRISMA 2020 Flow Diagram",
        "📋 Screening Decisions & Rationale",
        "📈 Evidence Tables & Risk of Bias",
        "🤖 Agent Audit Trail & State",
        "⏱️ Performance & Evaluation"
    ])

    with tab1:
        st.subheader("Generated Systematic Literature Review Manuscript")
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            st.download_button(
                "📥 Download Manuscript (.md)",
                data=state.get("final_report_markdown", ""),
                file_name=f"systematic_review_{state.get('research_topic', 'report')[:30].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                "📥 Download Raw State Data (.json)",
                data=json.dumps(state, indent=2, default=str),
                file_name="systematic_review_state.json",
                mime="application/json",
                use_container_width=True
            )
        st.markdown(state.get("final_report_markdown", "*No report generated.*"))

    with tab2:
        st.subheader("PRISMA 2020 Flow Diagram")
        st.caption("Flow of information through the different phases of the systematic review.")
        mermaid_code = generate_mermaid_flow_diagram(counts)
        st.code(mermaid_code, language="mermaid")
        
        c_flow1, c_flow2 = st.columns(2)
        with c_flow1:
            st.markdown("#### Database Identification Breakdown")
            for db, n in counts.get("db_counts", {}).items():
                st.write(f"- **{db}:** {n} studies")
            st.write(f"- **Duplicates Removed:** {counts.get('duplicates_removed', 0)}")
        with c_flow2:
            st.markdown("#### Screening & Eligibility")
            st.write(f"- **Title/Abstract Excluded:** {counts.get('records_excluded_ta', 0)}")
            st.write(f"- **Reports Assessed Full-Text:** {counts.get('reports_assessed_ft', 0)}")
            st.write(f"- **Final Included:** {counts.get('final_included', 0)}")

    with tab3:
        st.subheader("Transparent Screening Audit Trail")
        st.caption("Every study evaluated with explicit inclusion/exclusion reasoning according to PRISMA Item 8.")
        
        ta_studies = state.get("ta_screened_studies", [])
        if ta_studies:
            for i, s in enumerate(ta_studies, 1):
                status_icon = "✅ INCLUDED" if s.get("include_title_abstract") else "❌ EXCLUDED"
                with st.expander(f"{status_icon} | {s.get('title', 'Untitled')} ({s.get('year', 'n.d.')}) [{s.get('source', '')}]"):
                    st.write(f"**Authors:** {', '.join(s.get('authors', []))}")
                    st.write(f"**Decision:** {status_icon}")
                    st.write(f"**Rationale:** {s.get('reason_title_abstract', 'N/A')}")
                    if s.get("doi"):
                        st.write(f"**DOI:** {s.get('doi')}")
                    if s.get("url"):
                        st.markdown(f"[Link to Study Source]({s.get('url')})")
                    st.caption(f"**Abstract:** {s.get('abstract', '')[:600]}...")

    with tab4:
        st.subheader("Structured Evidence Tables & Quality Appraisal")
        evidence = state.get("extracted_evidence", [])
        quality = state.get("quality_assessments", [])

        if evidence:
            st.markdown("#### Methodological Characteristics")
            for e, q in zip(evidence, quality):
                with st.expander(f"📖 {e.get('title')} ({e.get('year')})"):
                    c_e1, c_e2 = st.columns(2)
                    with c_e1:
                        st.write(f"**Design:** {e.get('study_design')}")
                        st.write(f"**Multi-Agent Architecture:** {e.get('methodology_and_agents')}")
                        st.write(f"**Primary Findings:** {e.get('key_findings')}")
                    with c_e2:
                        bias = q.get("risk_of_bias", {})
                        st.write(f"**Overall Quality Rating:** `{bias.get('overall_quality_rating', 'Moderate')}`")
                        st.write(f"- Selection Bias: {bias.get('selection_bias', 'Low')}")
                        st.write(f"- Rigor: {bias.get('evaluation_rigor', 'Low')}")
                        st.write(f"- Rationale: {bias.get('rationale', '')}")

    with tab5:
        st.subheader("Agent Coordination Audit Trail")
        st.caption("Multi-Agent LangGraph execution traces and Critic loop decisions.")
        
        st.write(f"**Critic Verdict:** `{state.get('critic_verdict')}`")
        st.write(f"**Critic Feedback:** {state.get('critic_feedback')}")
        st.write(f"**Revision Loops Executed:** {state.get('revision_iteration', 0)}")
        
        st.divider()
        st.markdown("#### Step-by-Step Execution Log")
        for log_entry in state.get("audit_trail", []):
            st.markdown(f"- **[{log_entry.get('stage')}]:** {log_entry.get('action')}")

    with tab6:
        st.subheader("System Evaluation & Benchmark Results")
        st.caption("Quantitative metrics measuring completeness, consistency, and time savings.")
        
        if metrics:
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Completeness Score", f"{metrics.get('completeness_score')}%")
            e2.metric("Rationale Traceability", f"{metrics.get('rationale_traceability_pct')}%")
            e3.metric("Inter-Agent Agreement", f"{metrics.get('inter_agent_consistency_pct')}%")
            e4.metric("Time Savings vs Manual", metrics.get("time_savings_percentage"))

            st.markdown(f"""
            ### Benchmark Analysis
            - **Traditional Manual Review Time:** ~{metrics.get('manual_review_benchmark_hours')} human hours (Cochrane/PRISMA average).
            - **Autonomous Multi-Agent Runtime:** **{metrics.get('agentic_execution_seconds')} seconds**.
            - **Estimated Labor Time Saved:** **~{metrics.get('time_saved_hours')} hours** of research screening and data extraction.
            - **PRISMA 2020 Compliance Status:** `{state.get('prisma_checklist_report', {}).get('status', 'COMPLIANT')}`.
            """)
