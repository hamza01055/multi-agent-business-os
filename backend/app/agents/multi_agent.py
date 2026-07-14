"""Multi-Agent Workflow — supervisor pattern (LangGraph).

A supervisor LLM routes the task between specialist workers
(researcher / writer / analyst) until it decides to FINISH.
Guard-railed by a max hop count.
"""
import json
from langgraph.graph import StateGraph, END
from app.agents.state import SupervisorState
from app.agents.tools import kb_search
from app.services.llm import get_chat_model

WORKERS = ["researcher", "writer", "analyst"]
MAX_HOPS = 12


def build_workflow_graph(workspace_id: str):
    llm = get_chat_model(temperature=0.2)

    def supervisor(state: SupervisorState):
        history = "\n".join(f"{m['agent']}: {m['content'][:600]}" for m in state["messages"])
        resp = llm.invoke([
            ("system",
             "You are a supervisor routing work between agents: researcher (gathers facts), "
             "writer (drafts prose), analyst (numbers, pros/cons, structure). "
             'Reply with JSON only: {"next": "researcher|writer|analyst|FINISH", "instruction": "..."}'),
            ("user", f"Task: {state['task']}\n\nWork so far:\n{history or '(none)'}"),
        ])
        try:
            decision = json.loads(resp.content.strip().strip("`").removeprefix("json"))
        except (json.JSONDecodeError, AttributeError):
            decision = {"next": "FINISH", "instruction": ""}
        nxt = decision.get("next", "FINISH")
        if state["hops"] >= MAX_HOPS:
            nxt = "FINISH"
        return {"next": nxt, "hops": state["hops"] + 1,
                "messages": [{"agent": "supervisor", "content": decision.get("instruction", "")}]}

    def make_worker(name: str, system: str):
        def worker(state: SupervisorState):
            instruction = state["messages"][-1]["content"] if state["messages"] else state["task"]
            context = kb_search(workspace_id, instruction) if name == "researcher" else ""
            resp = llm.invoke([
                ("system", system),
                ("user", f"Overall task: {state['task']}\nYour instruction: {instruction}\n{context}"),
            ])
            return {"messages": [{"agent": name, "content": resp.content}]}
        return worker

    g = StateGraph(SupervisorState)
    g.add_node("supervisor", supervisor)
    g.add_node("researcher", make_worker("researcher", "You gather and cite facts. Use the provided context."))
    g.add_node("writer", make_worker("writer", "You write clear, polished prose based on prior findings."))
    g.add_node("analyst", make_worker("analyst", "You analyze: numbers, comparisons, risks, recommendations."))
    g.set_entry_point("supervisor")
    g.add_conditional_edges(
        "supervisor", lambda s: s["next"],
        {**{w: w for w in WORKERS}, "FINISH": END},
    )
    for w in WORKERS:
        g.add_edge(w, "supervisor")
    return g.compile()


def run_workflow(workspace_id: str, task: str) -> dict:
    graph = build_workflow_graph(workspace_id)
    result = graph.invoke({"task": task, "messages": [], "next": "", "hops": 0})
    trace = result["messages"]
    final = next((m["content"] for m in reversed(trace) if m["agent"] != "supervisor"), "")
    return {"result": final, "trace": trace}
