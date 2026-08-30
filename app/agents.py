import os
from langchain_cohere import ChatCohere
from .config import COHERE_API_KEY, COHERE_MODEL
from .models import SupplierEvaluation


class EvaluationAgent:
    """
    Evaluation Agent.

    Cohere judges proposal content only.
    It does not calculate weighted scores, benchmarks,
    gaps, PPI, ranking or tie-breaks.
    """

    def __init__(self, model_name: str = COHERE_MODEL):
        self.llm = ChatCohere(
            model=model_name,
            temperature=0,
            cohere_api_key=COHERE_API_KEY,
        )

        self.structured_llm = self.llm.with_structured_output(
            SupplierEvaluation
        )

    def evaluate(self, proposal_text: str, criteria: list):
        criteria_text = "\n\n".join(
            [
                f"""
Criterion ID: {criterion['criterion_id']}
Criterion: {criterion['name']}
What to inspect: {criterion['description']}
Maximum Score: {criterion['max_score']}
"""
                for criterion in criteria
            ]
        )

        prompt = f"""
You are an RFP Evaluation Agent.

Evaluate ONE supplier proposal against the active evaluation criteria.

Your role is ONLY to judge the content of the proposal.

You MUST NOT:
- calculate weighted scores
- calculate absolute weighted score
- calculate peer benchmarks
- calculate criterion gaps
- calculate relative percentages
- calculate PPI
- rank suppliers
- apply tie-break rules

Python will perform all arithmetic, benchmarking and ranking.

For EVERY active criterion return:
1. criterion_id
2. score
3. justification
4. evidence

Scoring:
- Score from 0 to the criterion maximum.
- Use ONLY information contained in the proposal.
- Never invent evidence.
- Missing information should reduce the score.
- Evidence should be specific.
- Be objective and consistent.

ACTIVE CRITERIA
===============
{criteria_text}

SUPPLIER PROPOSAL
=================
{proposal_text}
"""

        return self.structured_llm.invoke(prompt)
