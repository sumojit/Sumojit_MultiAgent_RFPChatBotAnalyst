def calculate_absolute_score(validation_result, criteria):
    results_by_id = {
        r["criterion_id"]: r
        for r in validation_result["criteria"]
    }

    absolute_score = 0.0
    criterion_results = []

    for criterion in criteria:
        criterion_id = criterion["criterion_id"]
        score = results_by_id[criterion_id]["normalized_score"]
        max_score = criterion["max_score"]
        weight = criterion["weight"]

        weighted_score = (score / max_score) * weight * 100
        absolute_score += weighted_score

        original = results_by_id[criterion_id]

        criterion_results.append({
            "criterion_id": criterion_id,
            "criterion_name": criterion["name"],
            "raw_score": original["raw_score"],
            "score": score,
            "max_score": max_score,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "justification": original["justification"],
            "evidence": original["evidence"],
            "warnings": original["warnings"],
        })

    return round(absolute_score, 4), criterion_results
