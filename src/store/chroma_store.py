from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

import chromadb

import sys
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config.settings import (
    CHROMA_GET_PAGE_SIZE,
    CHROMA_PERSIST_DIR,
    CHROMA_UPSERT_BATCH_SIZE,
    COLLECTION_NAME,
)


class PaperStore:
    def __init__(self, persist_dir: Optional[Path] = None, collection_name: str = COLLECTION_NAME):
        self._persist = Path(persist_dir or CHROMA_PERSIST_DIR)
        self._persist.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._persist))
        # Use Chroma's default ONNX MiniLM embedder (same 384-d model family as all-MiniLM-L6-v2).
        # SentenceTransformerEmbeddingFunction pulls PyTorch; broken torch installs often raise NameError: nn is not defined.
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self._collection.count()

    def add_papers(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0
        docs = []
        ids = []
        metas = []
        for _, row in df.iterrows():
            pid = str(row.get("pmid", row.name)).strip() or f"row_{row.name}"
            text = f"{row.get('title', '')} {row.get('abstract', '')}".strip()
            if not text:
                continue
            docs.append(text[:8000])
            ids.append(pid)
            metas.append(
                {
                    "title": str(row.get("title", ""))[:500],
                    "abstract": str(row.get("abstract", ""))[:4000],
                    "authors": str(row.get("authors", ""))[:500],
                    "journal": str(row.get("journal", ""))[:200],
                    "year": str(row.get("year", "")),
                    "pmid": pid,
                }
            )
        if not ids:
            return 0
        batch = max(50, CHROMA_UPSERT_BATCH_SIZE)
        for i in range(0, len(ids), batch):
            self._collection.upsert(
                documents=docs[i : i + batch],
                ids=ids[i : i + batch],
                metadatas=metas[i : i + batch],
            )
        return len(ids)

    def get_all(self) -> pd.DataFrame:
        n = self.count()
        if n == 0:
            return pd.DataFrame()
        page = max(100, CHROMA_GET_PAGE_SIZE)
        rows: List[Dict[str, Any]] = []
        offset = 0
        while offset < n:
            chunk = min(page, n - offset)
            raw = self._collection.get(
                include=["metadatas", "documents"],
                limit=chunk,
                offset=offset,
            )
            if not raw["ids"]:
                break
            for i, mid in enumerate(raw["ids"]):
                m = raw["metadatas"][i] if raw["metadatas"] else {}
                rows.append(
                    {
                        "pmid": m.get("pmid", mid),
                        "title": m.get("title", ""),
                        "abstract": m.get("abstract", raw["documents"][i] if raw.get("documents") else ""),
                        "authors": m.get("authors", ""),
                        "journal": m.get("journal", ""),
                        "year": m.get("year", ""),
                        "keywords": "",
                    }
                )
            offset += len(raw["ids"])
        return pd.DataFrame(rows)

    def search(self, query_texts: str, n_results: int = 10) -> List[Dict[str, Any]]:
        r = self._collection.query(query_texts=[query_texts], n_results=min(n_results, max(self.count(), 1)))
        out = []
        if not r["ids"] or not r["ids"][0]:
            return out
        for i, mid in enumerate(r["ids"][0]):
            m = r["metadatas"][0][i] if r["metadatas"] else {}
            dist = r["distances"][0][i] if r.get("distances") else 0
            out.append(
                {
                    "title": m.get("title", ""),
                    "abstract": m.get("abstract", ""),
                    "authors": m.get("authors", ""),
                    "journal": m.get("journal", ""),
                    "year": m.get("year", ""),
                    "pmid": m.get("pmid", mid),
                    "distance": float(dist),
                }
            )
        return out
