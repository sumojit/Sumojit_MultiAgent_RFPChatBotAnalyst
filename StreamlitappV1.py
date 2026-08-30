import os
import json
import streamlit as st
import pandas as pd
from app.db import initialize_database
from app.graph import build_graph


# ---------------------------------------------------------
# 🌟 INITIALIZE SESSION STATE KEYS (ADD THIS HERE)
# ---------------------------------------------------------
if "evaluation_complete" not in st.session_state:
    st.session_state["evaluation_complete"] = False

if "graph_state" not in st.session_state:
    st.session_state["graph_state"] = {}

if "rfp_run_id" not in st.session_state:
    st.session_state["rfp_run_id"] = "N/A"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hello! I am your Cohere Procurement Analyst. Ask me anything about the compiled graph evaluation data."}
    ]

# Setup page configuration
st.set_page_config(page_title="RFP Evaluation Suite", page_icon="📋", layout="wide")
st.title("📋 Multi-Agent RFP Evaluation Dashboard")

# # Ensure state variable is defined
# state = st.session_state["graph_state"]
# all_results = state.get("all_results", [])

# Pull API keys safely from environment variables or Streamlit secrets
COHERE_API_KEY = os.environ.get("COHERE_API_KEY") or st.secrets.get("COHERE_API_KEY")

# Reference view of criteria layout 
CRITERIA_DATA = [
    {"Criterion": "Technical Capability", "Weight": "30%", "Max Score": 100, "Description": "Architecture, integrations, scalability, technical fit"},
    {"Criterion": "Implementation Plan", "Weight": "20%", "Max Score": 100, "Description": "Timeline, milestones, staffing, risk plan"},
    {"Criterion": "Commercial Value", "Weight": "20%", "Max Score": 100, "Description": "Pricing clarity, total cost, assumptions"},
    {"Criterion": "Security & Compliance", "Weight": "20%", "Max Score": 100, "Description": "Controls, certifications, privacy, auditability"},
    {"Criterion": "Support & Experience", "Weight": "10%", "Max Score": 100, "Description": "Support model, similar projects, references"}
]

# Exact dictionary setup matching your original main entry script
SUPPLIERS = [
    {"supplier_name": "Apex Systems", "submission_date": "2026-08-25", "experience_rating": 8.5, "pdf_path": "data/sample_pdfs/apex_systems.pdf"},
    {"supplier_name": "BrightPath Tech", "submission_date": "2026-08-24", "experience_rating": 6.5, "pdf_path": "data/sample_pdfs/brightpath_tech.pdf"},
    {"supplier_name": "NexaWorks", "submission_date": "2026-08-26", "experience_rating": 9.0, "pdf_path": "data/sample_pdfs/nexaworks.pdf"},
    {"supplier_name": "Orbit Digital", "submission_date": "2026-08-23", "experience_rating": 9.5, "pdf_path": "data/sample_pdfs/orbit_digital.pdf"},
]

def run_rfp_evaluation(suppliers):
    """Triggers your real LangGraph compilation workflow."""
    initialize_database()
    app = build_graph()
    
    initial_state = {
        "suppliers": suppliers
    }
    
    # Invoke your actual LangGraph pipeline
    final_state = app.invoke(initial_state)
    return final_state

# --- APP NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Evaluation Criteria", 
    "📥 Supplier Input", 
    "🏆 Leaderboard", 
    "📊 Detailed Scorecard", 
    "⚙️ Run Details"
])

# --- TAB 1: CRITERIA ---
with tab1:
    st.header("Active Evaluation Criteria & Weights")
    st.write("These metrics govern the grading system executed by the database initialization layers.")
    st.table(pd.DataFrame(CRITERIA_DATA))

# --- TAB 2: SUPPLIER INPUT ---
with tab2:
    st.header("Supplier Proposal Ingestion")
    
    # Diagnostic sidebar checking if repository PDFs exist inside the environment
    st.sidebar.header("📁 Checked Supplier Data")
    all_files_exist = True
    for s in SUPPLIERS:
        if os.path.exists(s["pdf_path"]):
            st.sidebar.success(f"✔️ {s['supplier_name']} Located")
        else:
            st.sidebar.error(f"❌ {s['supplier_name']} Missing")
            all_files_exist = False

    if not COHERE_API_KEY:
        st.error("⚠️ `COHERE_API_KEY` missing! Configure it in Streamlit's settings dashboard.")
        st.stop()

    st.write("Click below to compile your multi-agent architecture and evaluate the target proposals:")
    evaluate_button = st.button("🚀 Execute LangGraph Evaluation Workflow", type="primary", disabled=not all_files_exist)

    if evaluate_button:
        with st.spinner("🧠 LangGraph agents are analyzing PDFs, extracting evidence, and scoring requirements..."):
            try:
                # 💥 EXECUTE REAL GRAPH PIPELINE 💥
                graph_output_state = run_rfp_evaluation(SUPPLIERS)
                
                # Store the dynamic final state dictionary into Streamlit's global session memory
                st.session_state["graph_state"] = graph_output_state
                st.session_state["evaluation_complete"] = True
                st.success("✅ LangGraph evaluation successfully completed! Use the tabs above to review metrics.")
            except Exception as e:
                st.error(f"An error occurred during runtime graph execution: {e}")

# ---------------------------------------------------------
# DYNAMICALLY LOAD METRICS IF EVALUATION RUN HAS COMPLETED
# ---------------------------------------------------------
if st.session_state.get("evaluation_complete", False):
    
    # 1. Safely extract the state dictionary returned by your nodes
    state = st.session_state["graph_state"]
    
    # 2. Extract your all_results array directly from the graph state
    all_results = state.get("all_results", [])
    
    # 3. Extract your rankings data
    live_rankings = state.get("rankings", [])
    
  
   # TAB 3: DYNAMIC LEADERBOARD, VISUAL ANALYTICS, & AI CHAT ---
    with tab3:
        st.header("🏆 Evaluation Results & Visual Analytics")
        
        live_rankings = state.get("rankings", [])
        if live_rankings:
            # 1. Summary Leaderboard Frame
            leaderboard_df = pd.DataFrame(live_rankings)
            if "criteria" in leaderboard_df.columns:
                leaderboard_df = leaderboard_df.drop(columns=["criteria"])
                
            st.subheader("Final Standing Summary")
            st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.subheader("📊 Interactive Analytical Charts")
            
            # --- PREPARE & FLATTEN DATA FOR SLICING ---
            # --- 🟢 FIX: PREPARE & FLATTEN DATA REGARDLESS OF DICTIONARY KEYS ---
            chart_rows = []
            for res in all_results:
                supp = res.get("supplier_name") or "Unknown Vendor"
                raw_criteria_list = res.get("criteria", [])
                
                # If it's a dictionary mapping (e.g., {"Technical": 85, "Security": 90})
                if isinstance(raw_criteria_list, dict):
                    for c_name, c_score in raw_criteria_list.items():
                        chart_rows.append({
                            "Supplier": supp,
                            "Criterion": str(c_name),
                            "Score": float(c_score if isinstance(c_score, (int, float)) else 0)
                        })
                
                # If it's a list of objects (e.g., [{"name": "Technical", "score": 85}])
                elif isinstance(raw_criteria_list, list):
                    for crit in raw_criteria_list:
                        if isinstance(crit, dict):
                            # Dynamically look for any common naming fields your scoring engine could use
                            c_name = (
                                crit.get("criterion_name") or 
                                crit.get("name") or 
                                crit.get("Criterion") or 
                                crit.get("criterion") or 
                                "Unknown Pillar"
                            )
                            c_score = crit.get("score") or crit.get("Score") or crit.get("value") or 0
                            chart_rows.append({
                                "Supplier": supp,
                                "Criterion": str(c_name),
                                "Score": float(c_score)
                            })
            
            flat_chart_df = pd.DataFrame(chart_rows)
            
            if not flat_chart_df.empty:
                col_ctrl1, col_ctrl2 = st.columns(2)
                with col_ctrl1:
                    selected_suppliers = st.multiselect(
                        "🔍 Filter & Compare Suppliers", 
                        options=flat_chart_df["Supplier"].unique(),
                        default=list(flat_chart_df["Supplier"].unique())
                    )
                with col_ctrl2:
                    selected_criteria = st.multiselect(
                        "📐 Filter Specific Evaluation Criteria",
                        options=flat_chart_df["Criterion"].unique(),
                        default=list(flat_chart_df["Criterion"].unique())
                    )
                
                filtered_chart_df = flat_chart_df[
                    (flat_chart_df["Supplier"].isin(selected_suppliers)) & 
                    (flat_chart_df["Criterion"].isin(selected_criteria))
                ]
                
                # Chart Display
                st.write("#### 📊 Scores Breakdown by Core Pillar")
                try:
                    pivot_df = filtered_chart_df.pivot(index="Criterion", columns="Supplier", values="Score")
                    st.bar_chart(pivot_df, height=350, use_container_width=True)
                except Exception:
                    st.info("Adjust filters to slice data metrics.")
            
            # ---------------------------------------------------------
            # 🤖 AI COPILOT CHATBOT AREA (NEW FUNCTIONALITY)
            # ---------------------------------------------------------
            st.write("---")
            st.subheader("🤖 Procurement AI Assistant")
            st.write("Ask questions regarding evaluation justifications, source evidence, gaps, or risks.")
            
            # 🟢 FIX 1: Initialize history with 'message' key instead of 'content'
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = [
                    {"role": "assistant", "message": "Hello! I am your Cohere Procurement Analyst. Ask me anything about the compiled graph evaluation data."}
                ]
            
            # Render chat container window with historical contexts
                        # Render chat container window with historical contexts safely
            chat_container = st.container(height=350, border=True)
            with chat_container:
                for msg in st.session_state["chat_history"]:
                    if isinstance(msg, dict):
                        # 🟢 SAFE FALLBACK: Pull whichever text field key is present
                        chat_text = msg.get("message") or msg.get("content") or ""
                        chat_role = msg.get("role", "assistant")
                        
                        # Only render if there is text present to prevent blank rows
                        if chat_text:
                            st.chat_message(chat_role).write(chat_text)
            
            # Accept user prompt input strings
            if user_prompt := st.chat_input("Ask a question about the supplier evaluations..."):
                # Instantly print user's entry bubble using the standardized key
                st.session_state["chat_history"].append({"role": "user", "message": user_prompt})
                chat_container.chat_message("user").write(user_prompt)
                
                with chat_container.chat_message("assistant"):
                    with st.spinner("Analyzing evaluation telemetry..."):
                        try:
                            import cohere
                            cohere_client = cohere.Client(api_key=COHERE_API_KEY)
                            
                            # Build the dynamic Context Packet to inform the LLM of current facts
                            evaluation_context = json.dumps(all_results, indent=2, default=str)
                            
                            # Compile system instructions grounding the chatbot in facts
                            system_instruction = (
                                "You are an expert procurement assistant. Answer user queries strictly using the provided "
                                "evaluation state telemetry context payload. If a fact cannot be verified from the context, "
                                "state that it was not surfaced by the evaluation agents.\n\n"
                                f"EVALUATION DATA METRICS:\n{evaluation_context}"
                            )
                            
                            # 🟢 FIX 2: Prepare clean historical log mappings directly using 'role' and 'message'
                            # In Cohere v5, you pass historical turns to chat_history, and the CURRENT prompt to 'message'.
                                                        # 🟢 FIX: Safely parse history elements regardless of their format
                            api_history = []
                            # Exclude the very last entry (which is the current user prompt turn)
                            for h in st.session_state["chat_history"][:-1]: 
                                if isinstance(h, dict):
                                    # Extract whatever text payload field is present safely
                                    history_text = h.get("message") or h.get("content") or ""
                                    
                                    if history_text:
                                        api_history.append({
                                            "role": "USER" if h.get("role", "").lower() == "user" else "CHATBOT",
                                            "message": history_text
                                        })
                            
                            # Execute API query line with corrected formatting parameters
                            response = cohere_client.chat(
                                message=user_prompt,
                                preamble=system_instruction,  
                                chat_history=api_history
                            )

                            
                            # Pull output string text
                            bot_reply = response.text
                            st.write(bot_reply)
                            st.session_state["chat_history"].append({"role": "assistant", "message": bot_reply})
                            
                        except Exception as chat_err:
                            error_msg = f"Failed to connect with Cohere Copilot service: {chat_err}"
                            st.error(error_msg)

    
    # --- TAB 4: DYNAMIC DETAILED SCORECARD ---
    with tab4:
        st.header("🔍 Granular Scorecard Analysis")
        
        if all_results:
            supplier_names = [res.get("supplier_name") for res in all_results if res.get("supplier_name")]
            selected_supplier = st.selectbox("Choose a Supplier to Inspect Matrix Breakdown", supplier_names)
            
            target_record = next((res for res in all_results if res.get("supplier_name") == selected_supplier), None)
            
            if target_record and "criteria" in target_record:
                st.subheader(f"Deep-dive Matrix: {selected_supplier}")
                
                # Metrics metric view panels
                kpi1, kpi2 = st.columns(2)
                with kpi1:
                    st.metric(label="Calculated Absolute Score", value=f"{target_record.get('absolute_score', 0.0):.2f} / 100")
                with kpi2:
                    st.metric(label="Supplier Baseline Experience", value=f"{target_record.get('experience_rating', 0.0)} / 10.0")
                
                # Display clean, un-nested interactive dataframes
                scorecard_df = pd.DataFrame(target_record["criteria"])
                st.dataframe(scorecard_df, use_container_width=True, hide_index=True)
            else:
                st.error(f"Could not parse explicit criterion rows for {selected_supplier}.")

    # --- TAB 5: DYNAMIC RUN DETAILS ---
    with tab5:
        st.header("System Execution Log & Run Metadata")
        
        col_run1, col_run2 = st.columns(2)
        with col_run1:
            # Displays the real runtime ID initialized by create_run_node()
            st.metric(label="RFP Run Unique Identifier", value=str(state.get("rfp_run_id", "N/A")))
        with col_run2:
            st.info("⚖️ **Tie-Break Rule Rule:** If absolute scores fall within close bands, the ranking tool weighs metrics alongside submission timestamps and baseline tenure properties.")
            
        # Export Payload Interface: Allows downloading the entire dynamic graph state dictionary directly as an audit file
        st.subheader("Export Run Manifest")
        st.download_button(
            label="📥 Download Run Evaluation JSON Payload",
            data=json.dumps(state, default=str, indent=4),
            file_name=f"rfp_run_{state.get('rfp_run_id', 'export')}.json",
            mime="application/json"
        )
else:
    with tab3: st.info("Run evaluation to view dynamic Leaderboard results.")
    with tab4: st.info("Run evaluation to view real scorecard rows.")
    with tab5: st.info("Run evaluation to check unique run metadata.")