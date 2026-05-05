from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional

from urllib.request import Request, urlopen

from config.settings import (
    LLM_SEARCH_MODEL,
    LLM_SEARCH_TIMEOUT_SECONDS,
    USE_LLM_SEARCH_ANSWER,
)


def _snippet(text: str, max_len: int = 520) -> str:
    s = " ".join(str(text or "").split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def normalize_hits_for_llm(
    hits_out: List[dict],
    *,
    max_docs: int = 8,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in hits_out[:max_docs]:
        t = item.get("type")
        if t == "chroma":
            h = item.get("hit") or {}
            out.append(
                {
                    "rank": item.get("rank", len(out) + 1),
                    "title": str(h.get("title") or "Untitled"),
                    "authors": str(h.get("authors") or ""),
                    "journal": str(h.get("journal") or ""),
                    "year": str(h.get("year") or ""),
                    "pmid": str(h.get("pmid") or "").strip(),
                    "abstract": _snippet(h.get("abstract") or "", 560),
                    "relevance": f"semantic distance {h.get('distance', 0):.4f}",
                }
            )
        elif t == "tfidf":
            row = item.get("row")
            sc = float(item.get("score") or 0.0)
            if row is None:
                continue
            get = row.get if hasattr(row, "get") else lambda k, d=None: d
            out.append(
                {
                    "rank": item.get("rank", len(out) + 1),
                    "title": str(get("title") or "Untitled"),
                    "authors": str(get("authors") or ""),
                    "journal": str(get("journal") or ""),
                    "year": str(get("year") or ""),
                    "pmid": str(get("pmid") or "").strip(),
                    "abstract": _snippet(get("abstract") or "", 560),
                    "relevance": f"TF‑IDF score {sc:.3f}",
                }
            )
    return out


def _build_user_prompt(query: str, docs: List[Dict[str, Any]]) -> str:
    lines = [
        "Use only the passages below. Markdown with sections:",
        "## Answer",
        "## Key points",
        "## How sources support this",
        "(reference [1], [2], …; say if evidence is thin.)",
        "",
        "Corpus:",
    ]
    for i, d in enumerate(docs, 1):
        lines.append(f"[{i}] {d.get('title', '')}")
        lines.append(f"    {d.get('authors', '')} · {d.get('journal', '')} {d.get('year', '')}")
        lines.append(f"    PMID {d.get('pmid', '')} · {d.get('relevance', '')}")
        lines.append(f"    {d.get('abstract', '')}")
        lines.append("")
    lines.append(f"Question: {query.strip()}")
    return "\n".join(lines)


def _call_openai_chat(system: str, user: str) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    body = {
        "model": LLM_SEARCH_MODEL,
        "temperature": 0.25,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    req = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=LLM_SEARCH_TIMEOUT_SECONDS) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="replace"))
    choices = payload.get("choices") or []
    if not choices:
        return None
    msg = choices[0].get("message") or {}
    content = str(msg.get("content") or "").strip()
    return content or None


def generate_literature_search_answer(
    query: str,
    hits_out: List[dict],
) -> Optional[str]:
    if not USE_LLM_SEARCH_ANSWER:
        return None
    docs = normalize_hits_for_llm(hits_out, max_docs=8)
    if not docs:
        return None
    system = "Biomedical retrieval QA: stick to the excerpts; flag gaps; no fabricated results."
    user = _build_user_prompt(query, docs)
    try:
        return _call_openai_chat(system, user)
    except Exception:
        return None


def format_retrieved_documents_markdown(
    hits_out: List[dict],
    *,
    pubmed_url_fn: Callable,
    max_docs: int = 10,
) -> str:
    docs = normalize_hits_for_llm(hits_out, max_docs=max_docs)
    if not docs:
        return "_No documents retrieved._"
    parts: List[str] = ["### Retrieved documents", ""]
    for d in docs:
        i = int(d.get("rank") or 0)
        title = _esc(str(d.get("title") or "Untitled"))
        pmid = str(d.get("pmid") or "").strip()
        url = pubmed_url_fn(pmid) if pmid and callable(pubmed_url_fn) else None
        link = f" [PubMed]({url})" if url else ""
        parts.append(f"**[{i}]** {title}{link}")
        parts.append(
            f"_{_esc(str(d.get('authors', '')))}_ · {_esc(str(d.get('journal', '')))} · {_esc(str(d.get('year', '')))}"
        )
        parts.append(f"*Score / note:* {_esc(str(d.get('relevance', '')))}")
        parts.append("")
        parts.append(d.get("abstract") or "")
        parts.append("")
    return "\n".join(parts)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
