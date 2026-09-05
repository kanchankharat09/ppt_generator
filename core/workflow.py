from typing import TypedDict

from langgraph.graph import END, StateGraph

from core.groq_client import generate_content_from_outline, plan_outline
from core.schemas import Outline, SlidePlan


class WorkflowState(TypedDict):
    input_text: str
    slide_count: int | None
    outline: Outline | None
    plan: SlidePlan | None


def plan_outline_node(state: WorkflowState) -> WorkflowState:
    outline = plan_outline(state["input_text"], slide_count=state["slide_count"])
    return {**state, "outline": outline}


def generate_content_node(state: WorkflowState) -> WorkflowState:
    plan = generate_content_from_outline(state["outline"], original_text=state["input_text"])
    return {**state, "plan": plan}


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("plan_outline", plan_outline_node)
    graph.add_node("generate_content", generate_content_node)

    graph.set_entry_point("plan_outline")
    graph.add_edge("plan_outline", "generate_content")
    graph.add_edge("generate_content", END)

    return graph.compile()


def run_generation_workflow(user_text: str, slide_count: int | None = None) -> SlidePlan:
    workflow = build_workflow()

    initial_state: WorkflowState = {
        "input_text": user_text,
        "slide_count": slide_count,
        "outline": None,
        "plan": None,
    }

    final_state = workflow.invoke(initial_state)
    return final_state["plan"]
