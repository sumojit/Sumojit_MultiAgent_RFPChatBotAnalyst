import os
import fitz
from langchain_core.tools import tool


@tool
def extract_pdf_text(pdf_path: str) -> str:
    """
    Document Tool: extract clean text from one supplier PDF.
    This tool does not evaluate the proposal.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)
    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")
            if text and text.strip():
                pages.append(
                    f"\n--- PAGE {page_number} ---\n{text.strip()}"
                )
    finally:
        document.close()

    if not pages:
        raise ValueError("PDF contains no readable text.")

    return "\n".join(pages)


@tool
def validate_evaluation(llm_result: dict, criteria: list) -> dict:
    """
    Validation Tool: validate and normalize LLM output.
    Missing criteria default to zero. Scores are clipped to valid ranges.
    """
    results_by_id = {
        item["criterion_id"]: item
        for item in llm_result.get("criteria", [])
    }

    validated = []

    for criterion in criteria:
        criterion_id = criterion["criterion_id"]
        max_score = criterion["max_score"]
        result = results_by_id.get(criterion_id)

        if result is None:
            validated.append({
                "criterion_id": criterion_id,
                "raw_score": None,
                "normalized_score": 0.0,
                "justification": "No evaluation returned.",
                "evidence": [],
                "warnings": [
                    "Missing criterion evaluation. Score defaulted to 0."
                ],
            })
            continue

        warnings = []
        raw_score = result.get("score")

        try:
            normalized_score = float(raw_score)
        except (TypeError, ValueError):
            normalized_score = 0.0
            warnings.append("Malformed score. Defaulted to 0.")

        if normalized_score < 0:
            normalized_score = 0.0
            warnings.append("Score below 0. Clipped to 0.")

        if normalized_score > max_score:
            normalized_score = max_score
            warnings.append(
                f"Score exceeded maximum {max_score}. Clipped to maximum."
            )

        evidence = result.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = [str(evidence)]
            warnings.append("Evidence was not a list. Converted to list.")

        justification = result.get("justification", "")
        if not isinstance(justification, str):
            justification = str(justification)
            warnings.append("Justification was not text.")

        validated.append({
            "criterion_id": criterion_id,
            "raw_score": raw_score,
            "normalized_score": normalized_score,
            "justification": justification,
            "evidence": evidence,
            "warnings": warnings,
        })

    return {"criteria": validated}


@tool
def calculate_ranking(supplier_results: list, criteria: list) -> list:
    """
    Ranking Tool: deterministic Python only.
    Calculates benchmark, gap, relative performance, PPI and rank.
    """
    benchmarks = {}

    for criterion in criteria:
        criterion_id = criterion["criterion_id"]
        max_score = criterion["max_score"]

        valid_scores = []
        for supplier in supplier_results:
            for result in supplier["criteria"]:
                if result["criterion_id"] == criterion_id:
                    score = result["score"]
                    if score is not None and 0 <= score <= max_score:
                        valid_scores.append(score)

        benchmarks[criterion_id] = max(valid_scores) if valid_scores else 0.0

    for supplier in supplier_results:
        ppi = 0.0

        for result in supplier["criteria"]:
            criterion_id = result["criterion_id"]
            score = result["score"]
            weight = result["weight"]
            benchmark = benchmarks[criterion_id]

            if benchmark == 0:
                relative_percentage = 100.0
            else:
                relative_percentage = (score / benchmark) * 100

            result["benchmark_score"] = round(benchmark, 4)
            result["criterion_gap"] = round(score - benchmark, 4)
            result["relative_percentage"] = round(relative_percentage, 4)

            ppi += relative_percentage * weight

        supplier["ppi"] = round(ppi, 4)

    ranked = sorted(
        supplier_results,
        key=lambda supplier: (
            -supplier["ppi"],
            supplier["submission_date"],
            -supplier["experience_rating"],
            supplier["supplier_name"].lower(),
        ),
    )

    for rank, supplier in enumerate(ranked, start=1):
        supplier["final_rank"] = rank

    return ranked
