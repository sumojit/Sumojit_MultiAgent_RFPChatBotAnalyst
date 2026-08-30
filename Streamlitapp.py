import os
import json
import uuid
import streamlit as st
import pandas as pd
from app.db import initialize_database
from app.graph import build_graph

# ==============================================================================
# 🎨 1. GLOBAL PAGE & ENTERPRISE STYLE DESIGN LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="RFP Intelligent Evaluation Suite", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection layer to clean up table styles, metric cards, and navigation headers
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #f1f3f5; border-radius: 6px 6px 0px 0px;
            padding: 8px 16px; font-weight: 600; color: #495057;
        }
        .stTabs [aria-selected="true"] { background-color: #2b6cb0 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 💾 2. STATE CACHE MANAGER INITIALIZATION
# ==============================================================================
if "evaluation_complete" not in st.session_state:
    st.session_state["evaluation_complete"] = False
if "graph_state" not in st.session_state:
    st.session_state["graph_state"] = {}
if "rfp_run_id" not in st.session_state:
    st.session_state["rfp_run_id"] = "N/A"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "message": "Hello! I am your Cohere Procurement Analyst. Ask me anything about the compiled graph evaluation data."}
    ]

# ==============================================================================
# 🔑 3. CONTROL SIDEBAR PANEL (USER CREDIENTIALS ENTRY & DISK DIAGNOSTICS)
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/artificial-intelligence.png", width=70)
    st.title("Control Panel")
    st.write("Configure workspace runtime authentication parameters securely below.")
    
    st.markdown("---")
    st.subheader("🔑 Authentication")
    
    # Prompt the user to enter their key directly via password hidden input fields
    user_cohere_key = st.text_input(
        "Cohere API Key", 
        type="password", 
        placeholder="cm_...",
        help="Obtain a workspace authorization signature string from dashboard.cohere.com"
    )
    
    # Prioritize dynamic web user entries, fallback to disk environment configuration models
    COHERE_API_KEY = user_cohere_key or os.environ.get("COHERE_API_KEY") or st.secrets.get("COHERE_API_KEY")

    st.markdown("---")
    st.subheader("📁 Checked Pipeline Data Assets")
    
    # Static initial asset structure array mapping to local supplier files
    SUPPLIERS = [
        {"supplier_name": "Apex Systems", "submission_date": "2026-08-25", "experience_rating": 8.5, "pdf_path": "data/sample_pdfs/apex_systems.pdf"},
        {"supplier_name": "BrightPath Tech", "submission_date": "2026-08-24", "experience_rating": 6.5, "pdf_path": "data/sample_pdfs/brightpath_tech.pdf"},
        {"supplier_name": "NexaWorks", "submission_date": "2026-08-26", "experience_rating": 9.0, "pdf_path": "data/sample_pdfs/nexaworks.pdf"},
        {"supplier_name": "Orbit Digital", "submission_date": "2026-08-23", "experience_rating": 9.5, "pdf_path": "data/sample_pdfs/orbit_digital.pdf"},
    ]
    
    all_files_exist = True
    for s in SUPPLIERS:
        if os.path.exists(s["pdf_path"]):
            st.success(f"✔️ {s['supplier_name']} Available")
        else:
            st.error(f"❌ {s['supplier_name']} Missing")
            all_files_exist = False

# ==============================================================================
# 🏗️ 4. APPLICATION WORKSPACE INTERFACE HEADER & DATA CONSTANTS
# ==============================================================================
st.title("🤖 Multi-Agent RFP Evaluation Suite")
st.caption("Engineered using LangGraph Multi-Agent Workflows & Grounded Cohere Intelligence Frameworks.")

CRITERIA_DATA = [
    {"Criterion": "Technical Capability", "Weight": "30%", "Max Score": 100, "Description": "Architecture, integrations, scalability, technical fit"},
    {"Criterion": "Implementation Plan", "Weight": "20%", "Max Score": 100, "Description": "Timeline, milestones, staffing, risk plan"},
    {"Criterion": "Commercial Value", "Weight": "20%", "Max Score": 100, "Description": "Pricing clarity, total cost, assumptions"},
    {"Criterion": "Security & Compliance", "Weight": "20%", "Max Score": 100, "Description": "Controls, certifications, privacy, auditability"},
    {"Criterion": "Support & Experience", "Weight": "10%", "Max Score": 100, "Description": "Support model, similar projects, references"}
]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Target Matrix Rules", 
    "📥 Ingestion Control", 
    "📊 Leaderboard & Analytics", 
    "🔍 Deep-Dive Scorecards", 
    "⚙️ Audit Execution Log"
])

# ------------------------------------------------------------------------------
# TAB 1: TARGET MATRIX CRITERIA RULES
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Active Weight Criteria Allocations")
    st.write("These strict parameters establish the evaluation weights applied across all incoming vendor documents.")
    st.dataframe(pd.DataFrame(CRITERIA_DATA), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 2: INGESTION CONTROL & GRAPH PIPELINE EXECUTION TRIGGER
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Proposal Processing Hub")
    st.write("Trigger your multi-agent architecture execution. This initializes tokenization engines, validates documents, and extracts metrics.")
    
    def run_rfp_evaluation(suppliers):
        initialize_database()
        app = build_graph()
        initial_state = {"suppliers": suppliers}
        return app.invoke(initial_state)

    # Halt orchestration loops if credentials are missing entirely from the layout
    if not COHERE_API_KEY:
        st.info("💡 Complete the authentication panel in the left sidebar to unlock the LangGraph evaluation pipeline controls.")
        evaluate_button = st.button("🚀 Execute LangGraph Evaluation Workflow", disabled=True)
    else:
        st.success("🔒 Authorization credentials staged successfully.")
        evaluate_button = st.button("🚀 Execute LangGraph Evaluation Workflow", type="primary", disabled=not all_files_exist)

    if evaluate_button:
        with st.spinner("🧠 Orchestrator Node activating Agent clusters... Parsing proposal text fragments and verifying criteria scores..."):
            try:
                # Trigger real LangGraph computation cluster workloads
                graph_output_state = run_rfp_evaluation(SUPPLIERS)
                
                # Persist state records inside the active memory caches
                st.session_state["graph_state"] = graph_output_state
                st.session_state["evaluation_complete"] = True
                st.session_state["rfp_run_id"] = str(graph_output_state.get("rfp_run_id", uuid.uuid4()))
                st.balloons()
                st.success("🎉 LangGraph network evaluation successfully completed! Review the analytics tabs below.")
            except Exception as e:
                st.error(f"Critical execution error during graph processing: {e}")

# ------------------------------------------------------------------------------
# TAB 3: VISUAL LEADERBOARD ANALYTICS & FAULT-TOLERANT AI COPILOT CHATBOT
# ------------------------------------------------------------------------------
with tab3:
    if st.session_state.get("evaluation_complete", False):
        state = st.session_state["graph_state"]
        all_results = state.get("all_results", [])
        live_rankings = state.get("rankings", [])
        
        st.subheader("🏆 Vendor Standings Summary")
        if live_rankings:
            # Flatten summary table views by stripping complex nested criteria dictionary rows
            leaderboard_df = pd.DataFrame(live_rankings)
            if "criteria" in leaderboard_df.columns:
                leaderboard_df = leaderboard_df.drop(columns=["criteria"])
            st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
            
            # --- PREPARE AND FLATTEN METRICS ARRAY FOR INTERACTIVE SLICING ---
            chart_rows = []
            for res in all_results:
                supp = res.get("supplier_name") or "Unknown Vendor"
                raw_crit = res.get("criteria", [])
                if isinstance(raw_crit, list):
                    for crit in raw_crit:
                        if isinstance(crit, dict):
                            c_name = crit.get("criterion_name") or crit.get("name") or crit.get("Criterion") or crit.get("criterion") or "Unknown"
                            c_score = crit.get("score") or crit.get("Score") or 0
                            chart_rows.append({"Supplier": supp, "Criterion": str(c_name), "Score": float(c_score)})
            
            flat_chart_df = pd.DataFrame(chart_rows)
            
            if not flat_chart_df.empty:
                st.markdown("---")
                st.subheader("📊 Slice & Dice Multidimensional Charts")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    sel_supp = st.multiselect("🔍 Filter Target Vendors", options=flat_chart_df["Supplier"].unique(), default=list(flat_chart_df["Supplier"].unique()))
                with col_c2:
                    sel_crit = st.multiselect("📐 Filter Specific Pillars", options=flat_chart_df["Criterion"].unique(), default=list(flat_chart_df["Criterion"].unique()))
                
                filtered_df = flat_chart_df[(flat_chart_df["Supplier"].isin(sel_supp)) & (flat_chart_df["Criterion"].isin(sel_crit))]
                
                # Render multi-vendor comparison bar plots
                try:
                    pivot_df = filtered_df.pivot(index="Criterion", columns="Supplier", values="Score")
                    st.bar_chart(pivot_df, height=380, use_container_width=True)
                except Exception:
                    st.caption("Adjust slicers to render complex matrix arrays.")
            
            # --- 🤖 FAULT-TOLERANT PROCUREMENT COHERE CHATBOT WINDOW ---
            st.markdown("---")
            st.subheader("🤖 Procurement AI Copilot Assistant")
            st.write("Ask questions regarding evaluation justifications, source evidence, gaps, or risks.")
            
            # Render conversation histories safely using flexible multi-key fallbacks
            chat_container = st.container(height=300, border=True)
            with chat_container:
                for msg in st.session_state["chat_history"]:
                    if isinstance(msg, dict):
                        chat_text = msg.get("message") or msg.get("content") or ""
                        if chat_text:
                            st.chat_message(msg.get("role", "assistant")).write(chat_text)
            
            if user_prompt := st.chat_input("Ask a question about the supplier evaluations..."):
                st.session_state["chat_history"].append({"role": "user", "message": user_prompt})
                chat_container.chat_message("user").write(user_prompt)
                
                with chat_container.chat_message("assistant"):
                    with st.spinner("Consulting evaluation states..."):
                        try:
                            import cohere
                            # Dynamically instantiate using the live active credentials marker
                            cohere_client = cohere.Client(api_key=COHERE_API_KEY)
                            
                            eval_ctx = json.dumps(all_results, indent=2, default=str)
                            system_instruction = f"You are an expert procurement assistant. Answer user queries strictly using the provided metrics context payload.\n\nDATA:\n{eval_ctx}"
                            
                            # Cleanly re-map past items safely avoiding rigid key crashes
                            api_history = []
                            for h in st.session_state["chat_history"][:-1]:
                                if isinstance(h, dict):
                                    t = h.get("message") or h.get("content") or ""
                                    if t:
                                        api_history.append({"role": "USER" if h.get("role", "").lower() == "user" else "CHATBOT", "message": t})
                            
                            # Submit query turns to Cohere backend API
                            response = cohere_client.chat(message=user_prompt, preamble=system_instruction, chat_history=api_history)
                            bot_reply = response.text
                            st.write(bot_reply)
                            st.session_state["chat_history"].append({"role": "assistant", "message": bot_reply})
                        except Exception as err:
                            st.error(f"Failed to communicate with Cohere Cloud endpoint API: {err}")
        else:
            st.info("Run evaluation execution steps to generate standings tables.")
    else:
        st.info("📢 Complete the LangGraph evaluation run inside the 'Ingestion Control' tab to populate interactive analytics dashboards.")

# ------------------------------------------------------------------------------
# TAB 4: DEEP-DIVE DRILLDOWN SCORECARDS
# ------------------------------------------------------------------------------
with tab4:
    if st.session_state.get("evaluation_complete", False):
        state = st.session_state["graph_state"]
        all_results = state.get("all_results", [])
        
        if all_results:
            supp_names = [res.get("supplier_name") for res in all_results if res.get("supplier_name")]
            chosen_supplier = st.selectbox("Choose a Supplier to Inspect Matrix Breakdown", list(set(supp_names)))
            
            rec = next((res for res in all_results if res.get("supplier_name") == chosen_supplier), None)
            if rec and "criteria" in rec:
                st.write(f"### Granular Evidence Matrix: {chosen_supplier}")
                
                # Visual Metric Cards Row layout
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric(label="Calculated Absolute Grade", value=f"{rec.get('absolute_score', 0.0):.2f} / 100")
                with mc2:
                    st.metric(label="Baseline Asset Rating", value=f"{rec.get('experience_rating', 0.0)} / 10.0")
                
                st.markdown("#### Criterion Verification Audit Trails")
                st.dataframe(pd.DataFrame(rec["criteria"]), use_container_width=True, hide_index=True)
    else:
        st.info("📢 Metrics breakdown records will generate following a successful evaluator run.")

# ------------------------------------------------------------------------------
# TAB 5: SYSTEM TRACKING AUDIT LOGGER DATA
# ------------------------------------------------------------------------------
with tab5:
    if st.session_state.get("evaluation_complete", False):
        state = st.session_state["graph_state"]
        
        st.subheader("System Execution Telemetry Log")
        st.metric(label="Active RFP Database Tracking Identifier (Run ID)", value=st.session_state.get("rfp_run_id", "N/A"))
        
        st.markdown("### Export Run Manifest")
        st.write("Extract the raw multi-agent dictionary output payload configuration mapping matrix directly as a standard JSON compliance document file.")
        st.download_button(
            label="📥 Download Run Evaluation JSON Payload",
            data=json.dumps(state, default=str, indent=4),
            file_name=f"rfp_audit_run_{st.session_state.get('rfp_run_id')}.json",
            mime="application/json"
        )
    else:
        st.info("📢 Run system analytics processing tasks to populate log tracking manifests.")
