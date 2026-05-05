import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from config.settings import (
    APP_PAGE_TITLE,
    PAGE_ADMIN_DASHBOARD,
    PAGE_ADMIN_PERMISSIONS,
    PAGE_INSTRUCTOR_DASHBOARD,
    PAGE_LITERATURE,
    PAGE_STUDENT_HOME,
    PUBMED_DEFAULT_RETRIEVE,
    PUBMED_MAX_RETRIEVE_CAP,
)
from src.app.admin_dashboard import render_admin_dashboard
from src.app.admin_ui import render_administration_panel
from src.app.auth_flow import (
    AUTH_DISABLE_ENV,
    auth_disabled,
    get_session_user,
    init_auth,
    logout,
    render_auth_screen,
)
from src.app.branding import (
    apply_query_param_logo_home,
    record_nav_history,
    render_branded_shell_header,
    sidebar_nav_key,
    try_show_streamlit_logo,
)
from src.app.instructor_dashboard import render_instructor_dashboard
from src.app.student_home import render_student_home
from src.app.theme import inject_app_theme


def pubmed_url(pmid) -> Optional[str]:
    if pd.isna(pmid):
        return None
    s = str(pmid).strip()
    return f"https://pubmed.ncbi.nlm.nih.gov/{s}/" if s.isdigit() else None


def _mark_pipeline_completed() -> None:
    st.session_state["last_pipeline_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def document_download_data(row: pd.Series, fmt: str = "csv") -> str:
    df_one = pd.DataFrame([row]).drop(columns=["_relevance", "_search_text"], errors="ignore")
    pmid = row.get("pmid")
    if pmid and pd.notna(pmid):
        u = pubmed_url(pmid)
        if u:
            df_one["pubmed_url"] = u
    return df_one.to_csv(index=False)


def _chroma_doc_count() -> Optional[int]:
    try:
        from src.store import PaperStore

        return int(PaperStore().count())
    except Exception:
        return None


def main():
    st.set_page_config(
        page_title=APP_PAGE_TITLE,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_app_theme()
    init_auth()

    user: Dict[str, Any]
    is_admin = False
    faculty_literature = False
    if auth_disabled():
        st.sidebar.markdown("### Role (guest mode)")
        ui_role = st.sidebar.radio(
            "Who is using the app?",
            ["Instructor / Researcher", "Student"],
            horizontal=True,
            help=f"Set {AUTH_DISABLE_ENV}=0 to require database login and fixed roles per account.",
        )
        faculty_literature = ui_role == "Instructor / Researcher"
        if faculty_literature:
            st.sidebar.text_input("Display name (optional)", key="disp_name", placeholder="For activity log")
        st.sidebar.caption(f"Auth off · set `{AUTH_DISABLE_ENV}` unset to use SQLite accounts.")
        user = {
            "id": 0,
            "username": "guest",
            "role": "instructor" if faculty_literature else "student",
            "display_name": (
                (st.session_state.get("disp_name") or "").strip()
                or ("Guest instructor" if faculty_literature else "Guest student")
            ),
            "is_active": True,
        }
    else:
        sess_user = get_session_user()
        if sess_user is None:
            render_auth_screen()
            st.stop()
        user = sess_user
        is_admin = user["role"] == "admin"
        faculty_literature = user["role"] in ("admin", "instructor")
        st.sidebar.markdown("### Account")
        st.sidebar.caption(f"**{user['username']}** · `{user['role']}`")
        if user["role"] == "instructor":
            st.sidebar.caption("Instructor: class tools and your student roster — no admin console.")
        elif is_admin:
            st.sidebar.caption("Administrator: use **Admin dashboard** and **Permissions & users** for accounts.")
        if st.sidebar.button("Sign out"):
            logout()
            st.rerun()
        if faculty_literature:
            st.sidebar.text_input(
                "Display name (optional)",
                key="disp_name",
                placeholder=str(user.get("display_name") or ""),
            )

    # Set up navigation key for Home/Back buttons
    nav_key = sidebar_nav_key(user, auth_disabled=auth_disabled())
    
    # Handle logo home navigation
    apply_query_param_logo_home(user, nav_key, auth_disabled=auth_disabled())
    
    # Render branded header with Home and Back buttons
    render_branded_shell_header(user, nav_key=nav_key, auth_disabled=auth_disabled())
    
    # Display sidebar logo
    try_show_streamlit_logo()

    from src.app.session_log import log_event
    from src.app.ui_sections import (
        render_nlp_analysis_section,
        render_web_application_portal,
        render_web_home_page,
    )
    from src.app.sample_data import get_full_sample_df

    st.sidebar.divider()

    page = PAGE_LITERATURE
    if not auth_disabled():
        uid = int(user["id"])
        if is_admin:
            page = st.sidebar.radio(
                "App page",
                [PAGE_ADMIN_DASHBOARD, PAGE_ADMIN_PERMISSIONS, PAGE_LITERATURE],
                key=f"ail_page_nav_adm_{uid}",
            )
        elif user["role"] == "instructor":
            page = st.sidebar.radio(
                "App page",
                [PAGE_INSTRUCTOR_DASHBOARD, PAGE_LITERATURE],
                key=f"ail_page_nav_ins_{uid}",
            )
        elif user["role"] == "student":
            page = st.sidebar.radio(
                "App page",
                [PAGE_STUDENT_HOME, PAGE_LITERATURE],
                key=f"ail_page_nav_stu_{uid}",
            )
    
    # Record navigation history for Back button
    record_nav_history(nav_key, page)

    lit_mode = auth_disabled() or page == PAGE_LITERATURE
    
    # Handle pending page navigation from Home/Back buttons
    pending_page = st.session_state.pop("_ail_pending_page", None)
    if pending_page:
        page = pending_page
        lit_mode = auth_disabled() or page == PAGE_LITERATURE
        st.rerun()

    results = None
    source_label = ""
    use_chroma_qa = False
    store = None
    src = None

    def _literature_sidebar_and_data() -> None:
        nonlocal results, source_label, use_chroma_qa, store, src

        if faculty_literature:
            st.sidebar.markdown("### Data source")
            full_sample = get_full_sample_df()
            st.sidebar.download_button(
                "Download CSV template",
                full_sample.to_csv(index=False),
                "sample_papers.csv",
                "text/csv",
                help="Expected columns: title, abstract, authors, journal, year, pmid, keywords",
            )
            st.sidebar.divider()
            pick = st.sidebar.radio(
                "Load papers via",
                [
                    "Fetch real data (PubMed API)",
                    "Use collection (ChromaDB)",
                    "Upload file (CSV/JSON)",
                ],
                label_visibility="collapsed",
            )
            if pick == "Fetch real data (PubMed API)":
                src = "pubmed"
            elif pick == "Use collection (ChromaDB)":
                src = "chroma"
            else:
                src = "upload"
        else:
            st.sidebar.markdown("### Your workspace")
            st.sidebar.caption(
                "Use the **class collection** or a **practice file** on this computer. "
                "Student role does not call PubMed."
            )
            pick_stu = st.sidebar.radio(
                "Choose",
                [
                    "Browse class collection (ChromaDB)",
                    "Practice file from my computer (CSV/JSON)",
                ],
                label_visibility="collapsed",
            )
            if pick_stu.startswith("Browse"):
                src = "chroma"
            else:
                src = "upload"
            with st.sidebar.expander("CSV format help"):
                st.markdown(
                    "Columns: **title**, **abstract**, **authors**, **journal**, **year**, **pmid** (optional). "
                    "Need at least **5** rows to run NLP."
                )

        if src == "pubmed":
            try:
                from src.store import PaperStore

                store = PaperStore()
            except Exception as e:
                st.sidebar.error(f"ChromaDB: {e}")
                st.stop()

            if "pubmed_results" in st.session_state:
                results = st.session_state["pubmed_results"]
                source_label = f"PubMed ({st.session_state.get('pubmed_n', 0)} papers)"
                st.sidebar.markdown("##### Loaded batch")
                lq = st.session_state.get("last_pubmed_query")
                if lq:
                    st.sidebar.caption(f"**Query used:** {lq[:100]}{'…' if len(lq) > 100 else ''}")
                st.sidebar.caption("Push to the shared vector store or clear and fetch again.")
                if st.sidebar.button("Clear PubMed session"):
                    for k in ["pubmed_results", "pubmed_n", "fetched_pmids_all"]:
                        st.session_state.pop(k, None)
                    st.rerun()
                if st.sidebar.button("Add this batch to ChromaDB", type="secondary"):
                    pm_df = results["papers_df"].drop(columns=["_relevance", "_search_text"], errors="ignore")
                    n = store.add_papers(pm_df)
                    log_event(f"PubMed → ChromaDB: {n} docs")
                    st.sidebar.success(f"Added {n} papers to the shared collection.")
            else:
                st.sidebar.markdown("##### PubMed search")
                with st.sidebar.expander("NCBI E-utilities (recommended)", expanded=False):
                    st.caption("PubMed asks for a contact email. Used only in API requests.")
                    st.text_input("Your email", key="entrez_email", placeholder="name@university.edu")
                q = st.sidebar.text_input(
                    "Search query", value="machine learning healthcare", help="Any PubMed query string"
                )
                mx = st.sidebar.number_input(
                    "Max papers to retrieve",
                    min_value=50,
                    max_value=PUBMED_MAX_RETRIEVE_CAP,
                    value=PUBMED_DEFAULT_RETRIEVE,
                    step=50,
                    help=(
                        f"Hard cap {PUBMED_MAX_RETRIEVE_CAP:,} PMIDs per run (well above 5,000). "
                        "IDs are relevance-ranked; large pulls are slow. Follow NCBI E-utilities usage (email, polite pacing)."
                    ),
                )
                fetched = st.session_state.get("fetched_pmids_all", set())
                if st.sidebar.button("Fetch from PubMed & run NLP", type="primary"):
                    if not q.strip():
                        st.sidebar.error("Enter a query.")
                    else:
                        from src.data_collection.pubmed_fetcher import fetch_pubmed_batch
                        from src.app.run_analysis import run_pipeline_on_dataframe

                        em = (st.session_state.get("entrez_email") or "").strip() or None
                        with st.spinner("PubMed + NLP pipeline…"):
                            df_fetched = fetch_pubmed_batch(q.strip(), max_results=int(mx), email=em)
                            if not df_fetched.empty:
                                df_fetched["pmid"] = df_fetched["pmid"].astype(str)
                                df_fetched = df_fetched[~df_fetched["pmid"].isin(fetched)]
                            if df_fetched.empty or len(df_fetched) < 5:
                                st.sidebar.error("Too few new papers — change query or size.")
                            else:
                                fetched.update(df_fetched["pmid"].unique())
                                st.session_state["fetched_pmids_all"] = fetched
                                st.session_state["pubmed_results"] = run_pipeline_on_dataframe(df_fetched)
                                st.session_state["pubmed_n"] = len(df_fetched)
                                st.session_state["last_pubmed_query"] = q.strip()[:200]
                                _mark_pipeline_completed()
                                log_event(f"PubMed fetch: n={len(df_fetched)}")
                                st.rerun()

        elif src == "chroma":
            try:
                from src.store import PaperStore

                store = PaperStore()
            except Exception as e:
                st.sidebar.error(f"ChromaDB: {e}")
                st.stop()
            n_total = store.count()
            st.sidebar.metric("Documents in shared collection", n_total)
            if n_total < 5:
                st.warning(
                    "The class collection is not ready yet (needs at least 5 documents). "
                    "Ask your instructor to load PubMed or uploads, or switch role if you are teaching."
                )
            else:
                ck, cc = "db_results", "db_results_n"
                refresh_label = "Re-run NLP on full collection" if faculty_literature else "Reload charts from collection"
                if st.sidebar.button(refresh_label):
                    if faculty_literature:
                        log_event("Refresh Chroma analysis")
                    st.session_state.pop(ck, None)
                    st.session_state.pop(cc, None)
                    st.rerun()
                if st.session_state.get(cc) == n_total and ck in st.session_state:
                    results = st.session_state[ck]
                else:
                    with st.spinner("Loading collection…"):
                        from src.app.run_analysis import run_pipeline_on_dataframe

                        results = run_pipeline_on_dataframe(store.get_all())
                        st.session_state[ck] = results
                        st.session_state[cc] = n_total
                        _mark_pipeline_completed()
                        if faculty_literature:
                            log_event(f"Chroma pipeline: {n_total} papers")
                source_label = f"Shared collection ({n_total} papers)"
                use_chroma_qa = True

        else:
            up = st.sidebar.file_uploader(
                "Paper file (CSV or JSON)" if faculty_literature else "Your practice file",
                type=["csv", "json"],
                help="Minimum 5 rows. Student uploads are analyzed in this browser session only.",
            )
            if "upload_results" in st.session_state:
                results = st.session_state["upload_results"]
                source_label = (
                    f"Uploaded file ({st.session_state.get('upload_n', 0)} papers)"
                    if faculty_literature
                    else f"Practice session ({st.session_state.get('upload_n', 0)} papers)"
                )
                if st.sidebar.button("Remove file from session"):
                    st.session_state.pop("upload_results", None)
                    st.session_state.pop("upload_n", None)
                    st.rerun()
                if faculty_literature:
                    try:
                        from src.store import PaperStore

                        if st.sidebar.button("Add this file to ChromaDB (shared)"):
                            s = PaperStore()
                            udf = results["papers_df"].drop(columns=["_relevance", "_search_text"], errors="ignore")
                            n = s.add_papers(udf)
                            log_event(f"Upload → Chroma: {n}")
                            st.sidebar.success(f"Added {n} to shared collection.")
                    except Exception:
                        pass
            elif up is not None:
                btn = "Run NLP on upload" if faculty_literature else "Run NLP on my file"
                if st.sidebar.button(btn, type="primary"):
                    from src.data_collection.io_utils import load_papers_from_bytes
                    from src.app.run_analysis import run_pipeline_on_dataframe

                    dfu = load_papers_from_bytes(up.getvalue(), up.name)
                    if len(dfu) < 5:
                        st.sidebar.error("Need at least 5 papers in the file.")
                    else:
                        st.session_state["upload_results"] = run_pipeline_on_dataframe(dfu)
                        st.session_state["upload_n"] = len(dfu)
                        _mark_pipeline_completed()
                        if faculty_literature:
                            log_event(f"Upload analyzed: {len(dfu)}")
                        st.rerun()
                st.info("Use **Run NLP** in the sidebar after choosing a file.")
                st.stop()
            else:
                st.info("Select a CSV or JSON file in the sidebar to continue.")
                st.stop()

    if lit_mode:
        _literature_sidebar_and_data()
    else:
        cn = _chroma_doc_count()
        if page == PAGE_ADMIN_DASHBOARD:
            render_admin_dashboard(chroma_doc_count=cn)
        elif page == PAGE_ADMIN_PERMISSIONS:
            render_administration_panel(actor_id=int(user["id"]))
        elif page == PAGE_INSTRUCTOR_DASHBOARD:
            render_instructor_dashboard(instructor_id=int(user["id"]), chroma_doc_count=cn)
        elif page == PAGE_STUDENT_HOME:
            render_student_home(user=user, chroma_doc_count=cn)
        return

    if results is not None:
        st.sidebar.success(f"Ready: **{source_label}**")

    def _web_application_block() -> None:
        web_nav = st.radio(
            "Web application",
            ["Home", "Analytics dashboard"],
            horizontal=True,
            label_visibility="collapsed",
            key="ail_web_application_nav",
        )
        if web_nav == "Home":
            render_web_home_page(
                user=user,
                is_instructor=faculty_literature,
                store=store,
                results=results,
                source_label=source_label or "—",
            )
        else:
            render_web_application_portal(
                results=results,
                source_label=source_label or "—",
                store=store,
                is_instructor=faculty_literature,
            )

    def _nlp_block() -> None:
        render_nlp_analysis_section(
            results,
            source_label=source_label or "—",
            use_chroma_qa=use_chroma_qa,
            store=store,
            pubmed_url_fn=pubmed_url,
            document_download_fn=document_download_data,
            is_instructor=faculty_literature,
        )

    tab_web, tab_nlp = st.tabs(["Web application", "NLP analysis"])
    with tab_web:
        _web_application_block()
    with tab_nlp:
        _nlp_block()


if __name__ == "__main__":
    main()
