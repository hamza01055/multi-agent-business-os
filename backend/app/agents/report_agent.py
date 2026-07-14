"""AI Report Generator — outline → sections → assembled markdown report.

Runs inside a Celery worker (sync LLM calls). Optionally grounds each
section in workspace documents via kb_search.
"""
from app.agents.tools import kb_search
from app.services.llm import get_chat_model

TEMPLATES = {
    "executive": ["Executive Summary", "Key Findings", "Analysis", "Risks", "Recommendations"],
    "technical": ["Overview", "Architecture", "Implementation Details", "Benchmarks", "Next Steps"],
    "marketing": ["Market Overview", "Audience", "Competitive Landscape", "Strategy", "KPIs"],
}


def generate_report(workspace_id: str, topic: str, template: str = "executive") -> str:
    llm = get_chat_model(temperature=0.3)
    sections = TEMPLATES.get(template, TEMPLATES["executive"])
    parts = [f"# {topic}\n"]
    for section in sections:
        context = kb_search(workspace_id, f"{topic} {section}")
        resp = llm.invoke([
            ("system", "Write one report section in markdown. Ground claims in the context when relevant; "
                       "cite sources in brackets. 150-300 words."),
            ("user", f"Report topic: {topic}\nSection: {section}\n\nContext:\n{context}"),
        ])
        parts.append(f"## {section}\n\n{resp.content}\n")
    return "\n".join(parts)
