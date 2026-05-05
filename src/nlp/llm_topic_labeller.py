from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from urllib.request import Request, urlopen

import pandas as pd

from config.settings import LLM_TOPIC_MODEL, LLM_TOPIC_TIMEOUT_SECONDS


def _build_prompt(topics_data: List[Dict[str, Any]], papers_df: pd.DataFrame) -> str:
    samples = (
        papers_df.get("title", pd.Series([], dtype=str))
        .fillna("")
        .astype(str)
        .head(15)
        .tolist()
    )
    lines = [
        "Name LDA topics from keywords + sample titles.",
        "JSON only: [{\"topic_id\": int, \"topic_name\": str}].",
        "2–5 words, title case; skip vague names.",
        "",
        "Titles:",
    ]
    lines.extend([f"- {t[:180]}" for t in samples if t])
    lines.append("")
    lines.append("Topics:")
    for t in topics_data:
        tid = int(t.get("topic_id", -1))
        words = ", ".join((t.get("words") or [])[:12])
        lines.append(f"- topic_id={tid}; terms={words}")
    return "\n".join(lines)


def _call_openai_for_labels(prompt: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return []

    body = {
        "model": LLM_TOPIC_MODEL,
        "input": prompt,
        "temperature": 0.2,
    }
    req = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=LLM_TOPIC_TIMEOUT_SECONDS) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="replace"))

    text = ""
    # Responses API may return output_text or structured output arrays.
    if isinstance(payload, dict):
        text = str(payload.get("output_text") or "")
        if not text:
            out = payload.get("output") or []
            chunks: List[str] = []
            for item in out:
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        chunks.append(str(c.get("text") or ""))
            text = "\n".join(chunks)
    if not text.strip():
        return []

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        return []
    return []


def apply_llm_topic_names(
    topics_data: List[Dict[str, Any]],
    papers_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    if not topics_data:
        return topics_data

    prompt = _build_prompt(topics_data, papers_df)
    try:
        labels = _call_openai_for_labels(prompt)
    except Exception:
        return topics_data
    if not labels:
        return topics_data

    name_by_id: Dict[int, str] = {}
    for row in labels:
        try:
            tid = int(row.get("topic_id"))
            name = str(row.get("topic_name") or "").strip()
            if tid >= 0 and name:
                name_by_id[tid] = name[:80]
        except Exception:
            continue

    out = []
    for t in topics_data:
        tt = dict(t)
        tid = int(tt.get("topic_id", -1))
        if tid in name_by_id:
            tt["topic_name"] = name_by_id[tid]
        out.append(tt)
    return out
