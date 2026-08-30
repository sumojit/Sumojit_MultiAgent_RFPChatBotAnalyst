from typing import Any, Dict, List, TypedDict
from pydantic import BaseModel, Field


class CriterionEvaluation(BaseModel):
    criterion_id: int = Field(description="ID of the evaluation criterion")
    score: float = Field(description="Score from 0 to the criterion maximum")
    justification: str = Field(description="Reason for the score")
    evidence: List[str] = Field(description="Specific evidence from the proposal")


class SupplierEvaluation(BaseModel):
    criteria: List[CriterionEvaluation]


class RFPState(TypedDict, total=False):
    rfp_run_id: int
    criteria: List[Dict[str, Any]]
    suppliers: List[Dict[str, Any]]
    all_results: List[Dict[str, Any]]
    rankings: List[Dict[str, Any]]
