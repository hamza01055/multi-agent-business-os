"""Tools shared by agents: workspace knowledge-base retrieval."""
from app.services.rag.vectorstore import similarity_search


def kb_search(workspace_id: str, query: str, k: int = 5) -> str:
    docs = similarity_search(workspace_id, query, k=k)
    if not docs:
        return "No relevant knowledge-base results."
    return "\n\n".join(
        f"[{d.metadata.get('source','kb')}#{d.metadata.get('chunk_no',0)}] {d.page_content}"
        for d in docs
    )
