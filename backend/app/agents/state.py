"""Shared agent state definitions (LangGraph)."""
from typing import Annotated, TypedDict
import operator


class ResearchState(TypedDict):
    question: str
    plan: list[str]                      # sub-questions
    findings: Annotated[list[str], operator.add]
    iterations: int
    max_iterations: int
    report: str


class SupervisorState(TypedDict):
    task: str
    messages: Annotated[list[dict], operator.add]  # {"agent": ..., "content": ...}
    next: str
    hops: int
