def display_results(final_state):
    rankings = final_state["rankings"]

    print("\n")
    print("=" * 90)
    print("FINAL RFP LEADERBOARD")
    print("=" * 90)

    print(
        f"{'Rank':<8}"
        f"{'Supplier':<25}"
        f"{'Absolute':<15}"
        f"{'PPI':<15}"
        f"{'Experience':<12}"
    )
    print("-" * 90)

    for supplier in rankings:
        print(
            f"{supplier['final_rank']:<8}"
            f"{supplier['supplier_name']:<25}"
            f"{supplier['absolute_score']:<15.2f}"
            f"{supplier['ppi']:<15.2f}"
            f"{supplier['experience_rating']:<12.1f}"
        )

    print("=" * 90)

    for supplier in rankings:
        print(f"\nSUPPLIER: {supplier['supplier_name']}")
        print(f"Final Rank: {supplier['final_rank']}")
        print(f"Absolute Score: {supplier['absolute_score']:.2f}")
        print(f"PPI: {supplier['ppi']:.2f}%")
        print("-" * 90)

        for result in supplier["criteria"]:
            print(f"\nCriterion: {result['criterion_name']}")
            print(
                f"Score: {result['score']:.2f} / "
                f"{result['max_score']:.2f}"
            )
            print(f"Weighted Score: {result['weighted_score']:.2f}")
            print(
                f"Benchmark: "
                f"{result.get('benchmark_score', 0):.2f}"
            )
            print(
                f"Gap: "
                f"{result.get('criterion_gap', 0):.2f}"
            )
            print(
                f"Relative Performance: "
                f"{result.get('relative_percentage', 0):.2f}%"
            )

            print("Justification:")
            print(result["justification"])

            print("Evidence:")
            for evidence in result["evidence"]:
                print(f"  - {evidence}")

            if result["warnings"]:
                print("Warnings:")
                for warning in result["warnings"]:
                    print(f"  - {warning}")
