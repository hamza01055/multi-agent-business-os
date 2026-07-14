"""Workspace-scoped vector store. FAISS by default, Milvus by config.

Layout (FAISS): {VECTOR_DIR}/{workspace_id}/index.faiss + metadata pickle.
Every chunk carries {doc_id, source, chunk_no} so retrieval can filter.
"""
import os
from langchain_community.vectorstores import FAISS
from app.core.config import settings
from app.services.llm import get_embeddings


def _ws_dir(workspace_id: str) -> str:
    d = os.path.join(settings.VECTOR_DIR, workspace_id)
    os.makedirs(d, exist_ok=True)
    return d


def _load(workspace_id: str) -> FAISS | None:
    d = _ws_dir(workspace_id)
    if not os.path.exists(os.path.join(d, "index.faiss")):
        return None
    return FAISS.load_local(d, get_embeddings(), allow_dangerous_deserialization=True)


def upsert_chunks(workspace_id: str, doc_id: str, source: str, chunks: list[str]) -> int:
    metadatas = [
        {"doc_id": doc_id, "source": source, "chunk_no": i} for i in range(len(chunks))
    ]
    store = _load(workspace_id)
    if store is None:
        store = FAISS.from_texts(chunks, get_embeddings(), metadatas=metadatas)
    else:
        store.add_texts(chunks, metadatas=metadatas)
    store.save_local(_ws_dir(workspace_id))
    return len(chunks)


def similarity_search(workspace_id: str, query: str, k: int = 6, doc_id: str | None = None):
    store = _load(workspace_id)
    if store is None:
        return []
    flt = {"doc_id": doc_id} if doc_id else None
    return store.similarity_search(query, k=k, filter=flt)
