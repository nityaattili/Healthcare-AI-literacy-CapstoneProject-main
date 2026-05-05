from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db.app_database import list_students_for_instructor_dashboard


def _roster_frame(rows: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(rows)
    show = df[
        [
            "username",
            "display_name",
            "is_active",
            "assigned_to_me",
            "supervisor_username",
            "last_login_at",
            "created_at",
        ]
    ].copy()
    show["is_active"] = show["is_active"].map({True: "yes", False: "no"})
    show["assigned_to_me"] = show["assigned_to_me"].map({True: "yes", False: "—"})
    show.columns = [
        "Username",
        "Display name",
        "Active",
        "Assigned to you",
        "Supervising instructor",
        "Last login",
        "Registered",
    ]
    return df, show


def render_instructor_dashboard(*, instructor_id: int, chroma_doc_count: Optional[int]) -> None:
    st.subheader("Instructor dashboard")
    st.caption(
        "Roster: your advisees plus students with no supervisor yet. "
        "Others’ advisees are hidden. Admins set supervisors under Permissions & users."
    )

    rows = list_students_for_instructor_dashboard(instructor_id)
    n = len(rows)
    n_mine = sum(1 for r in rows if r.get("assigned_to_me"))
    n_no_sup = sum(
        1 for r in rows if not r.get("supervisor_username") or r.get("supervisor_username") == "—"
    )
    n_on = sum(1 for r in rows if r.get("is_active"))

    a, b, c, d, e = st.columns(5)
    a.metric("In this list", n)
    b.metric("Yours", n_mine)
    c.metric("No supervisor", n_no_sup)
    d.metric("Active", n_on)
    e.metric("Chroma docs", chroma_doc_count if chroma_doc_count is not None else "—")

    st.caption(
        "Corpus charts and LDA topics: sidebar → **Literature & NLP**, load data, then "
        "**Web application** (dashboard) or **NLP analysis** (topics, keywords, graph, Search)."
    )

    if not rows:
        st.info("Nobody in this list yet.")
        return

    df, show = _roster_frame(rows)
    st.subheader("Roster")
    st.dataframe(show, use_container_width=True, hide_index=True, height=min(440, 36 * (len(show) + 2)))

    left, right = st.columns(2)
    pie_df = pd.DataFrame(
        {
            "label": ["Assigned to you", "Rest of this list"],
            "count": [n_mine, max(0, n - n_mine)],
        }
    )
    with left:
        fig_p = px.pie(
            pie_df,
            names="label",
            values="count",
            hole=0.45,
            color_discrete_sequence=["#0d9488", "#cbd5e1"],
        )
        fig_p.update_layout(height=300, margin=dict(t=16, b=16, l=16, r=16))
        st.plotly_chart(fig_p, use_container_width=True)

    status_df = pd.DataFrame({"Status": ["Active", "Inactive"], "Students": [n_on, n - n_on]})
    with right:
        fig_b = px.bar(
            status_df,
            x="Status",
            y="Students",
            color="Status",
            color_discrete_map={"Active": "#0d9488", "Inactive": "#94a3b8"},
            text="Students",
        )
        fig_b.update_traces(textposition="outside")
        fig_b.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=16, b=32, l=32, r=16),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_b, use_container_width=True)

    sup = df["supervisor_username"].fillna("—").replace("", "—").value_counts().head(12)
    if len(sup) > 0:
        st.subheader("Who supervises whom (this view)")
        sup_df = pd.DataFrame({"supervisor_username": sup.index.astype(str), "n": sup.values})
        fig_h = px.bar(
            sup_df,
            x="n",
            y="supervisor_username",
            orientation="h",
            labels={"n": "Students", "supervisor_username": "Supervisor"},
        )
        fig_h.update_traces(marker_color="#0d9488")
        fig_h.update_layout(
            height=min(340, 48 + 26 * len(sup)),
            margin=dict(t=12, b=32, l=12, r=12),
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig_h, use_container_width=True)

    if df["created_at"].notna().any():
        ts = pd.to_datetime(df["created_at"], errors="coerce").dropna()
        if len(ts):
            monthly = ts.dt.to_period("M").astype(str).value_counts().sort_index()
            fig_t = px.line(
                x=monthly.index,
                y=monthly.values,
                markers=True,
                labels={"x": "Month", "y": "New accounts"},
            )
            fig_t.update_traces(line_color="#0f766e", marker=dict(size=7))
            fig_t.update_layout(
                height=280,
                margin=dict(t=12, b=40, l=40, r=16),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_t, use_container_width=True)

    s_last = df["last_login_at"].astype(str)
    logged = df["last_login_at"].notna() & s_last.str.len().gt(0) & ~s_last.isin({"None", "nan", "NaT"})
    st.caption(
        f"{int(logged.sum())} / {n} have a stored last-login timestamp."
    )
