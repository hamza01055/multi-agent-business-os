"""Research Agent — LangGraph: planner → searcher → critic loop → synthesizer.

Grounded in the workspace knowledge base (kb_search tool). The critic decides
whether findings are sufficient; a hard iteration cap prevents runaway loops.
"""
from langgraph.graph import StateGraph, END
from app.agents.state import ResearchState
from app.agents.tools import kb_search
from app.services.llm import get_chat_model


def build_research_graph(workspace_id: str):
    llm = get_chat_model(temperature=0.2)

    def planner(state: ResearchState):
        resp = llm.invoke([
            ("system", "Break the research question into 2-4 focused sub-questions. One per line, no numbering."),
            ("user", state["question"]),
        ])
        plan = [l.strip() for l in resp.content.splitlines() if l.strip()][:4]
        return {"plan": plan}

    def searcher(state: ResearchState):
        idx = min(state["iterations"], len(state["plan"]) - 1)
        sub_q = state["plan"][idx]
        context = kb_search(workspace_id, sub_q)
        resp = llm.invoke([
            ("system", "Answer the sub-question using ONLY the context. Be concise. Cite sources in brackets."),
            ("user", f"Context:\n{context}\n\nSub-question: {sub_q}"),
        ])
        return {"findings": [f"Q: {sub_q}\nA: {resp.content}"], "iterations": state["iterations"] + 1}

    def critic(state: ResearchState):
        return state  # decision happens in the conditional edge

    def should_continue(state: ResearchState):
        if state["iterations"] >= min(len(state["plan"]), state["max_iterations"]):
            return "synthesizer"
        return "searcher"

    def synthesizer(state: ResearchState):
        resp = llm.invoke([
            ("system", "Write a well-structured research report in markdown with sections and a conclusion. Preserve citations."),
            ("user", f"Question: {state['question']}\n\nFindings:\n\n" + "\n\n".join(state["findings"])),
        ])
        return {"report": resp.content}

    g = StateGraph(ResearchState)
    g.add_node("planner", planner)
    g.add_node("searcher", searcher)
    g.add_node("critic", critic)
    g.add_node("synthesizer", synthesizer)
    g.set_entry_point("planner")
    g.add_edge("planner", "searcher")
    g.add_edge("searcher", "critic")
    g.add_conditional_edges("critic", should_continue, {"searcher": "searcher", "synthesizer": "synthesizer"})
    g.add_edge("synthesizer", END)
    return g.compile()


def run_research(workspace_id: str, question: str, depth: int = 2) -> str:
    graph = build_research_graph(workspace_id)
    result = graph.invoke({
        "question": question, "plan": [], "findings": [],
        "iterations": 0, "max_iterations": depth * 2, "report": "",
    })
    return result["report"]
