from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db.app_database import list_users_admin


def render_admin_dashboard(*, chroma_doc_count: Optional[int]) -> None:
    st.markdown("### Administrator dashboard")
    st.caption("Live counts from the SQLite user directory and shared literature index.")

    users = list_users_admin()
    df = pd.DataFrame(users) if users else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total accounts", len(users))
    c2.metric("Active", int(df["is_active"].sum()) if not df.empty else 0)
    c3.metric("Pending approval", int((~df["is_active"]).sum()) if not df.empty else 0)
    c4.metric("ChromaDB documents", chroma_doc_count if chroma_doc_count is not None else "—")

    if df.empty:
        st.info("No user records yet. Use **Permissions & users** to create accounts.")
        return

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### Accounts by role")
        role_counts = df.groupby("role").size().reset_index(name="count")
        fig1 = px.bar(
            role_counts,
            x="role",
            y="count",
            color="role",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig1.update_layout(showlegend=False, height=320, margin=dict(t=24, b=40))
        st.plotly_chart(fig1, use_container_width=True)

    with r2:
        st.markdown("##### Active vs inactive")
        act = df.groupby(df["is_active"].map({True: "Active", False: "Inactive"})).size().reset_index(name="count")
        act.columns = ["status", "count"]
        fig2 = px.pie(act, names="status", values="count", hole=0.45, color_discrete_sequence=["#0d9488", "#cbd5e1"])
        fig2.update_layout(height=320, margin=dict(t=24, b=24))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Sign-ups over time (by day)")
    try:
        df["day"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
        daily = df.dropna(subset=["day"]).groupby("day").size().reset_index(name="new_users")
        if not daily.empty:
            fig3 = px.line(daily, x="day", y="new_users", markers=True)
            fig3.update_layout(height=280, margin=dict(t=24, b=40))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.caption("No parseable registration dates.")
    except Exception:
        st.caption("Could not build timeline chart.")

    st.markdown("##### Instructors & student assignments")
    sup_col = "supervisor_username" if "supervisor_username" in df.columns else None
    if sup_col:
        sub = df[df["role"] == "student"].copy()
        if not sub.empty:
            vc = sub[sup_col].fillna("(unassigned)").value_counts().head(12).reset_index()
            vc.columns = ["supervisor", "students"]
            fig4 = px.bar(vc, x="students", y="supervisor", orientation="h", color="students", color_continuous_scale="Teal")
            fig4.update_layout(height=min(360, 40 + 28 * len(vc)), showlegend=False, margin=dict(l=20, r=20, t=24, b=20))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.caption("No student rows yet.")
    else:
        st.caption("Supervisor column not available — run the app once to migrate the database.")
