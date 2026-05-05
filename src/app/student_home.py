from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st


def render_student_home(*, user: Dict[str, Any], chroma_doc_count: Optional[int]) -> None:
    st.markdown("### Student home")
    name = user.get("display_name") or user.get("username") or "there"
    st.success(f"Signed in as **{name}** (`{user.get('username', '')}`).")

    c1, c2 = st.columns(2)
    c1.metric("Shared literature collection", chroma_doc_count if chroma_doc_count is not None else "—")
    c2.caption("Open **Literature & NLP** in the sidebar to browse the class corpus or upload a practice file.")

    st.markdown(
        "**Next:** Sidebar → **Literature & NLP**. Either **Browse class collection** or "
        "upload a **Practice file** (CSV/JSON, at least 5 rows). "
        "Then open **Web application** / **NLP analysis** for charts and Q&A."
    )
    st.caption("Admins and instructors use other sidebar pages; you only see student routes.")
