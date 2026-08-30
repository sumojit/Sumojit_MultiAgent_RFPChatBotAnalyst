from langgraph.graph import StateGraph, START, END

from .agents import EvaluationAgent
from .db import (
    create_run,
    load_active_criteria,
    persist_results,
    validate_criteria,
)
from .models import RFPState
from .scoring import calculate_absolute_score
from .tools import (
    calculate_ranking,
    extract_pdf_text,
    validate_evaluation,
)


def load_criteria_node(state: RFPState):
    print("\n[ORCHESTRATOR] Loading active criteria...")
    criteria = load_active_criteria()
    validate_criteria(criteria)
    state["criteria"] = criteria
    print(f"Loaded {len(criteria)} active criteria.")
    return state


def create_run_node(state: RFPState):
    print("\n[ORCHESTRATOR] Creating RFP run...")
    run_id = create_run(state["criteria"])
    state["rfp_run_id"] = run_id
    print(f"Created RFP Run ID: {run_id}")
    return state


def evaluate_suppliers_node(state: RFPState):
    criteria = state["criteria"]
    suppliers = state["suppliers"]

    print("\n[ORCHESTRATOR] Starting supplier evaluation...")

    evaluation_agent = EvaluationAgent()
    all_results = []

    for index, supplier in enumerate(suppliers, start=1):
        supplier_name = supplier["supplier_name"]
        pdf_path = supplier["pdf_path"]

        print("\n" + "=" * 70)
        print(f"SUPPLIER {index}: {supplier_name}")
        print("=" * 70)

        print("\n[DOCUMENT TOOL] Extracting PDF text...")
        proposal_text = extract_pdf_text.invoke({"pdf_path": pdf_path})
        print(f"Extracted {len(proposal_text)} characters.")

        print("\n[EVALUATION AGENT] Cohere evaluating proposal...")
        llm_result = evaluation_agent.evaluate(proposal_text, criteria)
        llm_result_dict = llm_result.model_dump()
        print("[EVALUATION AGENT] Evaluation received.")

        print("\n[VALIDATION TOOL] Validating LLM response...")
        validation_result = validate_evaluation.invoke({
            "llm_result": llm_result_dict,
            "criteria": criteria,
        })
        print("[VALIDATION TOOL] Validation complete.")

        absolute_score, criterion_results = calculate_absolute_score(
            validation_result,
            criteria,
        )

        print(f"Absolute Score: {absolute_score:.2f}")

        all_results.append({
            "supplier_name": supplier_name,
            "submission_date": supplier["submission_date"],
            "experience_rating": supplier["experience_rating"],
            "absolute_score": absolute_score,
            "criteria": criterion_results,
        })

    state["all_results"] = all_results
    return state


def rank_suppliers_node(state: RFPState):
    print("\n[ORCHESTRATOR] Calling Ranking Tool...")
    rankings = calculate_ranking.invoke({
        "supplier_results": state["all_results"],
        "criteria": state["criteria"],
    })
    state["rankings"] = rankings
    print("[RANKING TOOL] Ranking completed.")
    return state


def persist_results_node(state: RFPState):
    print("\n[ORCHESTRATOR] Persisting results...")
    persist_results(state["rfp_run_id"], state["rankings"])
    print(f"Results stored for Run ID {state['rfp_run_id']}.")
    return state


def build_graph():
    graph = StateGraph(RFPState)

    graph.add_node("load_criteria", load_criteria_node)
    graph.add_node("create_run", create_run_node)
    graph.add_node("evaluate_suppliers", evaluate_suppliers_node)
    graph.add_node("rank_suppliers", rank_suppliers_node)
    graph.add_node("persist_results", persist_results_node)

    graph.add_edge(START, "load_criteria")
    graph.add_edge("load_criteria", "create_run")
    graph.add_edge("create_run", "evaluate_suppliers")
    graph.add_edge("evaluate_suppliers", "rank_suppliers")
    graph.add_edge("rank_suppliers", "persist_results")
    graph.add_edge("persist_results", END)

    return graph.compile()
