import html as html_module
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from config.settings import (
    KEYWORD_TOP_N,
    KEYWORD_TREND_CHART_LINES,
    N_TOPICS,
    USE_LLM_SEARCH_ANSWER,
)
from src.nlp.llm_search_answer import (
    format_retrieved_documents_markdown,
    generate_literature_search_answer,
)
from src.app.session_log import get_activity_log


def _safe_df(x: Any) -> pd.DataFrame:
    return x if isinstance(x, pd.DataFrame) else pd.DataFrame()


def _corpus_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"n": 0}
    n = len(df)
    abs_col = df["abstract"] if "abstract" in df.columns else pd.Series([""] * n, index=df.index)
    short_abs = (abs_col.fillna("").astype(str).str.len() < 30).sum()
    if "year" in df.columns:
        yr = pd.to_numeric(df["year"], errors="coerce")
        pct_miss_year = round(100.0 * float(yr.isna().mean()), 1)
    else:
        pct_miss_year = 100.0
    dup = 0
    if "pmid" in df.columns:
        dup = int(df["pmid"].astype(str).str.strip().duplicated().sum())
    uj = int(df["journal"].nunique()) if "journal" in df.columns else 0
    med_tok = 0.0
    if "tokens" in df.columns:
        lens = df["tokens"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        med_tok = round(float(lens.median()), 1) if len(lens) else 0.0
    return {
        "n": n,
        "pct_short_abstract": round(100.0 * short_abs / n, 1),
        "pct_missing_year": pct_miss_year,
        "duplicate_pmids": dup,
        "unique_journals": uj,
        "median_tokens": med_tok,
    }


def _keyword_strength_trends_figure(
    keyword_trends: pd.DataFrame,
    *,
    max_lines: int,
    height: int = 540,
):
    """Line chart of keyword strength by year with dashed links for correlated term pairs."""
    import plotly.express as px

    if keyword_trends.empty or "year" not in keyword_trends.columns:
        return None
    if not {"keyword", "score"}.issubset(keyword_trends.columns):
        return None
    top_kw = keyword_trends.groupby("keyword")["score"].sum().nlargest(max_lines).index
    sub = keyword_trends[keyword_trends["keyword"].isin(top_kw)]
    if sub.empty:
        return None
    fig = px.line(
        sub,
        x="year",
        y="score",
        color="keyword",
        markers=True,
    )
    fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=5))
    fig.update_layout(
        title=dict(
            text=(
                "<b>Keyword strength by year</b><br><sup>From titles/abstracts in your corpus. "
                "Teal dashed segments connect pairs of terms whose yearly scores move similarly "
                "(Pearson r on the year grid).</sup>"
            ),
            x=0.5,
            xanchor="center",
        ),
        yaxis_title="Keyword strength (relative)",
        xaxis_title="Year",
        legend=dict(
            title="",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=9),
        ),
        margin=dict(l=56, r=200, t=110, b=52),
        height=height,
        plot_bgcolor="#f8fafc",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    fig.add_annotation(
        text="<b>Relation between keywords</b>",
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.09,
        showarrow=False,
        font=dict(size=12, color="#0f766e"),
        align="center",
    )
    pivot = sub.pivot_table(index="year", columns="keyword", values="score", aggfunc="sum").fillna(0.0)
    if pivot.shape[0] >= 3 and pivot.shape[1] >= 2:
        corr = pivot.corr(numeric_only=True)
        cols = list(corr.columns)
        pairs: List[Tuple[str, str, float]] = []
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                v = corr.iloc[i, j]
                if pd.notna(v):
                    pairs.append((cols[i], cols[j], float(v)))
        pairs.sort(key=lambda t: -abs(t[2]))
        last_y = pivot.index.max()
        added = 0
        for ka, kb, r in pairs:
            if added >= 4 or abs(r) < 0.28:
                break
            if last_y not in pivot.index:
                break
            y0 = float(pivot.loc[last_y, ka])
            y1 = float(pivot.loc[last_y, kb])
            if y0 <= 0 or y1 <= 0:
                continue
            fig.add_shape(
                type="line",
                x0=float(last_y),
                y0=y0,
                x1=float(last_y),
                y1=y1,
                line=dict(color="rgba(5, 150, 105, 0.55)", width=2.5, dash="dash"),
                layer="below",
            )
            added += 1
    return fig


def _hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="ail-shell"><div class="ail-hero"><h1>{title}</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def _metric_cards(items: List[Tuple[str, str, str]]) -> None:
    cells = "".join(
        f'<div class="ail-card"><div class="ail-card-label">{lab}</div>'
        f'<div class="ail-card-value">{val}</div>'
        f'<div class="ail-card-sub">{sub}</div></div>'
        for lab, val, sub in items
    )
    st.markdown(f'<div class="ail-shell"><div class="ail-grid">{cells}</div></div>', unsafe_allow_html=True)


def _section(title: str) -> None:
    st.markdown(f'<div class="ail-shell"><div class="ail-section-title">{title}</div></div>', unsafe_allow_html=True)


def _two_col_html(left_title: str, left_html: str, right_title: str, right_html: str) -> None:
    st.markdown(
        f'<div class="ail-shell"><div class="ail-row-2">'
        f'<div class="ail-card ail-status-ok"><strong>{left_title}</strong><br/><br/>{left_html}</div>'
        f'<div class="ail-card ail-status-info"><strong>{right_title}</strong><br/><br/>{right_html}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _instructor_paper_detail_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    out = df.copy()
    if "abstract" in out.columns:
        abs_s = out["abstract"].fillna("").astype(str)
    else:
        abs_s = pd.Series([""] * len(out), index=out.index)
    out["_abstract_len"] = abs_s.str.len()
    if "tokens" in out.columns:
        out["_token_n"] = out["tokens"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    else:
        out["_token_n"] = 0
    if "year" in out.columns:
        yr = pd.to_numeric(out["year"], errors="coerce")
    else:
        yr = pd.Series([pd.NA] * len(out), index=out.index, dtype=float)
    out["_year_ok"] = yr.notna()
    out["_abs_ok"] = out["_abstract_len"] >= 30
    return out


def render_web_home_page(
    *,
    user: Dict[str, Any],
    is_instructor: bool,
    store: Any,
    results: Optional[dict[str, Any]],
    source_label: str,
) -> None:
    r = str(user.get("role") or "")
    if r == "admin":
        role_label = "Administrator"
    elif is_instructor:
        role_label = "Instructor / Researcher"
    else:
        role_label = "Student"
    name = html_module.escape(str(user.get("display_name") or user.get("username") or "User"))
    extra = (
        " Use the <strong>Administration</strong> tab to manage accounts and permissions."
        if r == "admin"
        else ""
    )
    st.markdown(
        f'<div class="ail-shell"><div class="ail-hero"><h1>Welcome, {name}</h1>'
        f"<p>You are signed in as <strong>{role_label}</strong>. "
        f"Use <strong>Analytics dashboard</strong> for KPIs and charts, and <strong>NLP analysis</strong> for topics, "
        f"networks, and <strong>Search</strong>.{extra}</p></div></div>",
        unsafe_allow_html=True,
    )

    ch_n = "—"
    if store is not None:
        try:
            ch_n = str(store.count())
        except Exception:
            pass
    corpus_ready = results is not None
    n_papers = len(_safe_df(results.get("papers_df"))) if corpus_ready else 0

    _metric_cards(
        [
            ("Your role", role_label, "from your account"),
            ("Shared collection", ch_n, "documents in ChromaDB"),
            ("Active corpus", str(n_papers) if corpus_ready else "—", "papers in current NLP run"),
            ("Data source", (source_label[:42] + "…") if len(source_label) > 44 else source_label or "—", "sidebar selection"),
        ]
    )

    _section("What you can do here")
    if r == "admin":
        _two_col_html(
            "Administration tab",
            "Approve <strong>self-service registrations</strong>, create users, set roles (admin / instructor / student), "
            "reset passwords, activate or deactivate accounts.",
            "Web & NLP",
            "Admins have instructor-level access to PubMed, uploads, and the shared ChromaDB collection, plus full analytics.",
        )
    elif is_instructor:
        _two_col_html(
            "Dashboard + literature",
            "<strong>Instructor dashboard</strong> lists students you see. "
            "<strong>Literature & NLP</strong> is where PubMed / Chroma / uploads live.",
            "NLP tab",
            "Topics, keywords, graph, and <strong>Search</strong> sit next to the web tab. No admin screens on your login.",
        )
    else:
        _two_col_html(
            "Web · Analytics dashboard",
            "Same analytics views as instructors for the <strong>dataset you load</strong> (class collection or practice file).",
            "NLP analysis tab",
            "Explore themes, trends, and connections; use <strong>Search</strong> over the loaded corpus.",
        )

    if r != "instructor":
        _section("Data storage")
        st.markdown(
            '<div class="ail-shell"><div class="ail-card ail-status-info">'
            "<strong>SQLite</strong> (<code>data/app_users.db</code>) is the <strong>system of record</strong> for users, "
            "password hashes, roles, and activation state. New registrations stay <strong>inactive</strong> until an admin approves them. "
            "<strong>ChromaDB</strong> (<code>data/chroma/</code>) holds <strong>shared literature embeddings</strong> only — separate from login data."
            "</div></div>",
            unsafe_allow_html=True,
        )


def render_web_application_portal(
    *,
    results: Optional[dict[str, Any]],
    source_label: str,
    store: Any,
    is_instructor: bool,
) -> None:
    if not is_instructor:
        _hero(
            "Learning portal",
            "Explore the **class literature collection** or analyze a **practice file** from your computer. "
            "Your practice uploads stay in this session only. Open **NLP analysis** for topics, trends, networks, and **Search**.",
        )

    ch_count = "—"
    if store is not None:
        try:
            ch_count = str(store.count())
        except Exception:
            pass

    if results is None:
        if is_instructor:
            st.markdown("### Instructor · analytics dashboard")
            st.caption(
                f"Shared collection: **{ch_count}** documents · Load a corpus from the sidebar to populate metrics and paper tables."
            )
            if store is not None:
                try:
                    st.metric("ChromaDB collection size", int(ch_count) if ch_count != "—" else 0)
                except ValueError:
                    pass
        else:
            st.markdown("### Learning portal · Web application")
            st.caption(
                f"Shared collection: **{ch_count}** documents · Choose **Browse class collection** or a **practice file** "
                "in the sidebar (≥5 papers). Charts and metrics appear here after the corpus loads."
            )
            if store is not None:
                try:
                    st.metric("Documents in shared collection", int(ch_count) if ch_count != "—" else 0)
                except ValueError:
                    pass
        return

    papers_df = _safe_df(results.get("papers_df"))
    topics_data = results.get("topics_data") if isinstance(results.get("topics_data"), list) else []
    year_stats_df = _safe_df(results.get("year_stats_df"))
    author_stats_df = _safe_df(results.get("author_stats_df"))
    journal_stats_df = _safe_df(results.get("journal_stats_df"))
    cocitation_edges = _safe_df(results.get("cocitation_edges"))
    keywords_data = results.get("keywords_data") if isinstance(results.get("keywords_data"), list) else []
    keyword_trends_df = _safe_df(results.get("keyword_trends"))

    n_papers = len(papers_df) if not papers_df.empty else 0
    n_topics = len(topics_data)
    n_edges = len(cocitation_edges) if not cocitation_edges.empty else 0
    n_kw = len(keywords_data) if keywords_data else 0

    last_run = st.session_state.get("last_pipeline_at", "—")
    if is_instructor:
        st.markdown("### Instructor · analytics dashboard")
        st.caption(
            f"**{source_label}** · Pipeline **{last_run}** · Shared store **{ch_count}** docs · "
            f"Use **NLP analysis** for deep dives (graph, **Search** tab)."
        )
    else:
        st.markdown("### Learning portal · Web application")
        st.caption(
            f"**{source_label}** · Last update **{last_run}** · Shared collection **{ch_count}** docs · "
            "Full **metrics, maps, and tables** below for your loaded dataset. Use **NLP analysis** for topics, "
            "networks, document list, and **Search**."
        )

    _section("Corpus KPIs")
    y_min, y_max = None, None
    if "year" in papers_df.columns and not papers_df.empty:
        yr = pd.to_numeric(papers_df["year"], errors="coerce").dropna()
        if len(yr):
            y_min, y_max = int(yr.min()), int(yr.max())
    span_txt = f"{y_min}–{y_max}" if y_min is not None else "—"
    _metric_cards(
        [
            ("Papers", str(n_papers), "in this analysis run"),
            ("LDA topics", str(n_topics), "latent themes"),
            ("Similarity edges", str(n_edges), "content graph"),
            ("Ranked keywords", str(n_kw), "TF-IDF top terms"),
            ("Year span", span_txt, "from metadata"),
            ("Unique journals", str(journal_stats_df["journal"].nunique()) if not journal_stats_df.empty else "0", "distinct venues"),
        ]
    )

    abs_lens = (
        papers_df["abstract"].fillna("").astype(str).str.len()
        if not papers_df.empty and "abstract" in papers_df.columns
        else pd.Series(dtype=int)
    )
    title_lens = (
        papers_df["title"].fillna("").astype(str).str.len()
        if not papers_df.empty and "title" in papers_df.columns
        else pd.Series(dtype=int)
    )
    pmid_pct = 0.0
    if not papers_df.empty and "pmid" in papers_df.columns:
        pmid_pct = round(
            100.0
            * float(papers_df["pmid"].astype(str).str.strip().str.match(r"^[0-9]+$", na=False).mean()),
            1,
        )
    share_top_journal = "—"
    if not journal_stats_df.empty and "count" in journal_stats_df.columns and n_papers:
        share_top_journal = f"{round(100.0 * float(journal_stats_df.iloc[0]['count']) / n_papers, 1)}%"
    n_nodes_g = 0
    if not cocitation_edges.empty and "source" in cocitation_edges.columns:
        n_nodes_g = len(set(cocitation_edges["source"].astype(str)) | set(cocitation_edges["target"].astype(str)))
    n_author_slots = int(author_stats_df["count"].sum()) if not author_stats_df.empty and "count" in author_stats_df.columns else 0

    _section("Corpus KPIs (extended)")
    _metric_cards(
        [
            ("Mean abstract length", f"{int(abs_lens.mean())} ch" if len(abs_lens) else "—", "characters"),
            ("Median title length", f"{int(title_lens.median())} ch" if len(title_lens) else "—", "characters"),
            ("PMID coverage", f"{pmid_pct}%", "numeric IDs"),
            ("Top journal share", share_top_journal, "of corpus"),
            ("Graph nodes", str(n_nodes_g), "in similarity map"),
            ("Author mentions", str(n_author_slots), "sum of author–paper links"),
        ]
    )

    _section("Distribution analytics")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("##### Publications by year")
        if not year_stats_df.empty and "year" in year_stats_df.columns:
            cdf = year_stats_df.set_index("year")
            col = "count" if "count" in cdf.columns else cdf.columns[0]
            st.bar_chart(cdf[col], height=260)
        else:
            st.caption("No year distribution.")
    with g2:
        st.markdown("##### Top venues")
        if not journal_stats_df.empty and "journal" in journal_stats_df.columns and "count" in journal_stats_df.columns:
            import plotly.express as px

            j15 = journal_stats_df.head(15).iloc[::-1]
            fig = px.bar(
                j15,
                x="count",
                y="journal",
                orientation="h",
                height=280,
                labels={"count": "Papers", "journal": ""},
            )
            fig.update_layout(showlegend=False, margin=dict(l=0, r=8, t=8, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No journal field.")
    with g3:
        st.markdown("##### Top weighted keywords")
        if keywords_data:
            import plotly.express as px

            kdf = pd.DataFrame(keywords_data)
            if "keyword" in kdf.columns and "score" in kdf.columns:
                kdf = kdf.copy()
                kdf["keyword"] = (
                    kdf["keyword"].fillna("").astype(str).str.strip().replace("", "(unnamed)")
                )
                kdf["score"] = pd.to_numeric(kdf["score"], errors="coerce").fillna(0.0)
                kdf = kdf.sort_values("score", ascending=True)
                n_kw_chart = len(kdf)
                # Fit all bars: ~14px per row, cap to avoid absurd DOM size on huge lists.
                chart_h = int(min(2200, max(280, 14 * n_kw_chart + 40)))
                fig2 = px.bar(
                    kdf,
                    x="score",
                    y="keyword",
                    orientation="h",
                    height=chart_h,
                    labels={"score": "Score", "keyword": ""},
                )
                fig2.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=8, t=8, b=0),
                    yaxis=dict(tickfont=dict(size=10)),
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("No keywords.")

    _section("Maps & longitudinal signals")
    import plotly.express as px
    import plotly.graph_objects as go

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("##### Venue share (treemap)")
        if not journal_stats_df.empty and "journal" in journal_stats_df.columns and "count" in journal_stats_df.columns:
            jt = journal_stats_df.head(30).copy()
            jt["journal"] = jt["journal"].astype(str).str.slice(0, 60)
            fig_tm = px.treemap(jt, path=["journal"], values="count", color="count", color_continuous_scale="Blues")
            fig_tm.update_layout(margin=dict(l=0, r=0, t=8, b=0), height=360)
            st.plotly_chart(fig_tm, use_container_width=True)
        else:
            st.caption("No journal counts.")
    with m2:
        st.markdown("##### Publications by year × top venues")
        if (
            not papers_df.empty
            and "journal" in papers_df.columns
            and "year" in papers_df.columns
            and not journal_stats_df.empty
        ):
            pj = papers_df.copy()
            pj["year"] = pd.to_numeric(pj["year"], errors="coerce")
            top_j = (
                journal_stats_df.head(12)["journal"].fillna("(Unknown)").astype(str).str.strip()
            )
            top_j = [j for j in top_j.tolist() if j]
            pj2 = pj[pj["journal"].astype(str).isin(top_j)].dropna(subset=["year"])
            if not pj2.empty:
                pivot_raw = (
                    pj2.assign(journal=pj2["journal"].fillna("(Unknown)").astype(str).str.strip())
                    .groupby(["journal", "year"])
                    .size()
                    .unstack(fill_value=0)
                    .sort_index()
                )
                if not pivot_raw.empty:
                    # Keep a stable, fully numeric matrix for imshow to avoid dtype/label edge-case errors.
                    pivot_vals = pivot_raw.to_numpy(dtype=float)
                    fig_hm = px.imshow(
                        pivot_vals,
                        labels=dict(x="Year", y="Journal", color="Papers"),
                        x=[str(int(c)) if pd.notna(c) else "" for c in pivot_raw.columns],
                        y=pivot_raw.index.astype(str).tolist(),
                        aspect="auto",
                        color_continuous_scale="YlGnBu",
                    )
                    fig_hm.update_layout(margin=dict(l=0, r=0, t=8, b=0), height=360)
                    st.plotly_chart(fig_hm, use_container_width=True)
                else:
                    st.caption("Not enough year–journal pairs.")
            else:
                st.caption("Not enough year–journal pairs.")
        else:
            st.caption("Need journal and year on papers.")

    m3, m4 = st.columns(2)
    with m3:
        st.markdown("##### Keyword strength over time")
        if (
            not keyword_trends_df.empty
            and "year" in keyword_trends_df.columns
            and "keyword" in keyword_trends_df.columns
            and "score" in keyword_trends_df.columns
        ):
            fig_kw = _keyword_strength_trends_figure(
                keyword_trends_df,
                max_lines=min(KEYWORD_TREND_CHART_LINES, 20),
                height=380,
            )
            if fig_kw is not None:
                fig_kw.update_layout(margin=dict(l=48, r=160, t=100, b=40))
                st.plotly_chart(fig_kw, use_container_width=True)
        else:
            st.caption("No keyword trend series (run pipeline on ≥2 papers with years).")
    with m4:
        st.markdown("##### Similarity / co-occurrence map (preview)")
        if not cocitation_edges.empty and "source" in cocitation_edges.columns and "target" in cocitation_edges.columns:
            try:
                import networkx as nx

                edge_sub = cocitation_edges.copy()
                if "weight" in edge_sub.columns and len(edge_sub) > 100:
                    edge_sub = edge_sub.nlargest(100, "weight")
                elif len(edge_sub) > 100:
                    edge_sub = edge_sub.head(100)
                G = nx.from_pandas_edgelist(edge_sub, "source", "target", edge_attr="weight")
                pos = nx.spring_layout(G, k=0.5, iterations=40, seed=42)
                edge_x, edge_y = [], []
                for e in G.edges():
                    x0, y0 = pos[e[0]]
                    x1, y1 = pos[e[1]]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]
                nx_ = [pos[n][0] for n in G.nodes()]
                ny = [pos[n][1] for n in G.nodes()]
                fig_g = go.Figure()
                fig_g.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=0.35, color="#94a3b8")))
                fig_g.add_trace(
                    go.Scatter(
                        x=nx_,
                        y=ny,
                        mode="markers",
                        marker=dict(size=6, color="#2563eb"),
                        text=[str(n)[:24] for n in G.nodes()],
                        hoverinfo="text",
                    )
                )
                fig_g.update_layout(
                    showlegend=False,
                    height=360,
                    margin=dict(l=10, r=10, t=8, b=10),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                )
                st.plotly_chart(fig_g, use_container_width=True)
                st.caption(f"Up to 100 strongest edges · {G.number_of_nodes()} nodes shown.")
            except Exception as ex:
                st.caption(f"Graph preview unavailable: {ex}")
        else:
            st.caption("No edges — corpus may be too small or uniform.")

    _section("Detailed tables")
    dt1, dt2, dt3, dt4 = st.tabs(["By year", "Journals", "Keywords", "Graph edges"])
    with dt1:
        if not year_stats_df.empty:
            st.dataframe(year_stats_df, use_container_width=True, hide_index=True, height=320)
        else:
            st.caption("No year aggregation.")
    with dt2:
        if not journal_stats_df.empty:
            st.dataframe(journal_stats_df.head(80), use_container_width=True, hide_index=True, height=320)
        else:
            st.caption("No journal stats.")
    with dt3:
        if keywords_data:
            st.dataframe(pd.DataFrame(keywords_data).head(80), use_container_width=True, height=320)
        else:
            st.caption("No global keyword ranking.")
        if not keyword_trends_df.empty:
            st.markdown("**Keyword trends (long)**")
            st.dataframe(keyword_trends_df.sort_values(["year", "keyword"]), use_container_width=True, height=260)
    with dt4:
        if not cocitation_edges.empty:
            st.dataframe(cocitation_edges.head(150), use_container_width=True, hide_index=True, height=320)
            st.caption("Directed/co-occurrence-style pairs from the analytics layer.")
        else:
            st.caption("No edge list.")

    qm = _corpus_quality_metrics(papers_df)
    _section("Quality & risk signals")
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Thin abstract", f"{qm['pct_short_abstract']}%", help="< 30 characters")
    q2.metric("Missing year", f"{qm['pct_missing_year']}%")
    q3.metric("Duplicate PMID", str(qm["duplicate_pmids"]))
    q4.metric("Median tokens", str(qm["median_tokens"]) if qm["n"] else "—")
    q5.metric("Top author (count)", str(int(author_stats_df.iloc[0]["count"])) if not author_stats_df.empty else "—")

    _section("LDA topic snapshot")
    if topics_data:
        rows = []
        for t in topics_data:
            rows.append(
                {
                    "topic": t.get("topic_name") or f"Topic {t.get('topic_id', 0)}",
                    "topic_id": t.get("topic_id", 0),
                    "documents": int(t.get("documents", 0)),
                    "citation_count": int(t.get("citation_count", 0)),
                    "top_terms": ", ".join((t.get("words") or [])[:12]),
                }
            )
        show_df = pd.DataFrame(rows)
        if not show_df.empty and "citation_count" in show_df.columns and int(show_df["citation_count"].sum()) == 0:
            st.caption("Citation values unavailable in source metadata; showing local corpus graph scores where possible.")
        st.dataframe(show_df, use_container_width=True, hide_index=True, height=min(280, 44 * (len(rows) + 1)))
    else:
        st.caption("No topic model output.")

    _section("Paper registry & search")
    reg = _instructor_paper_detail_table(papers_df)
    if reg.empty:
        st.caption("No papers in frame.")
    else:
        q_search = st.text_input(
            "Filter by title / PMID / journal / authors",
            "",
            key="paper_registry_search_inst" if is_instructor else "paper_registry_search_stu",
        )
        disp = reg.copy()
        if "authors" in disp.columns:
            disp["authors"] = disp["authors"].astype(str).str.slice(0, 140)
        if "tokens" in disp.columns:
            disp["token_preview"] = disp["tokens"].apply(
                lambda xs: ", ".join(xs[:14]) if isinstance(xs, list) and xs else ""
            )
        show_cols = [
            "pmid",
            "year",
            "journal",
            "authors",
            "title",
            "token_preview",
            "_abstract_len",
            "_token_n",
            "_year_ok",
            "_abs_ok",
        ]
        disp = disp[[c for c in show_cols if c in disp.columns]].copy()
        disp = disp.rename(
            columns={
                "_abstract_len": "abstract_chars",
                "_token_n": "tokens",
                "_year_ok": "has_year",
                "_abs_ok": "abstract_ok",
            }
        )
        if q_search.strip():
            m = (
                disp["title"].astype(str).str.contains(q_search, case=False, na=False)
                if "title" in disp.columns
                else pd.Series(True, index=disp.index)
            )
            if "pmid" in disp.columns:
                m = m | disp["pmid"].astype(str).str.contains(q_search, case=False, na=False)
            if "journal" in disp.columns:
                m = m | disp["journal"].astype(str).str.contains(q_search, case=False, na=False)
            if "authors" in disp.columns:
                m = m | disp["authors"].astype(str).str.contains(q_search, case=False, na=False)
            disp = disp[m]
        st.dataframe(disp.head(200), use_container_width=True, height=360)
        _reg_cap = f"Up to 200 rows shown of {len(disp)} matches."
        if is_instructor:
            _reg_cap += " Full CSV/JSON exports: **Downloads & session log** below."
        st.caption(_reg_cap)

    _section("Papers flagged for review")
    reg2 = _instructor_paper_detail_table(papers_df)
    if not reg2.empty and "_abs_ok" in reg2.columns and "_year_ok" in reg2.columns:
        flag_cols = [c for c in ("pmid", "year", "journal", "title") if c in reg2.columns]
        bad = reg2[(~reg2["_abs_ok"]) | (~reg2["_year_ok"])][flag_cols].head(50)
        if bad.empty:
            st.success("No missing-year or thin-abstract flags in the first 50 checks.")
        else:
            st.dataframe(bad, use_container_width=True, hide_index=True, height=min(320, 38 * (len(bad) + 1)))
    else:
        st.caption("No flag data.")

    _section("Author concentration (top 15)")
    if not author_stats_df.empty:
        st.dataframe(author_stats_df.head(15), use_container_width=True, hide_index=True, height=380)
    else:
        st.caption("No author stats.")

    if is_instructor:
        with st.expander("Downloads & session log", expanded=False):
            summary = {
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "source_label": source_label,
                "quality": qm,
                "lda_topics": topics_data,
                "pipeline_params": {"n_topics_target": N_TOPICS, "keyword_top_n": KEYWORD_TOP_N},
            }
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button(
                    "pipeline_summary.json",
                    json.dumps(summary, indent=2, default=str),
                    file_name="pipeline_summary.json",
                    mime="application/json",
                    key="dl_pipe_summary",
                )
                st.download_button(
                    "lda_topics.json",
                    json.dumps(topics_data, indent=2),
                    file_name="lda_topics.json",
                    mime="application/json",
                    key="dl_topics_json",
                )
            with c2:
                if keywords_data:
                    st.download_button(
                        "keywords_top.csv",
                        pd.DataFrame(keywords_data).to_csv(index=False),
                        file_name="keywords_top.csv",
                        mime="text/csv",
                        key="dl_kw_csv",
                    )
                if not author_stats_df.empty:
                    st.download_button(
                        "authors_top.csv",
                        author_stats_df.head(80).to_csv(index=False),
                        file_name="authors_top.csv",
                        mime="text/csv",
                        key="dl_auth_csv",
                    )
                if not keyword_trends_df.empty:
                    st.download_button(
                        "keyword_trends.csv",
                        keyword_trends_df.to_csv(index=False),
                        file_name="keyword_trends.csv",
                        mime="text/csv",
                        key="dl_kw_trends_csv",
                    )
                if not cocitation_edges.empty:
                    st.download_button(
                        "similarity_edges.csv",
                        cocitation_edges.to_csv(index=False),
                        file_name="similarity_edges.csv",
                        mime="text/csv",
                        key="dl_edges_csv",
                    )
                if not year_stats_df.empty:
                    st.download_button(
                        "year_stats.csv",
                        year_stats_df.to_csv(index=False),
                        file_name="year_stats.csv",
                        mime="text/csv",
                        key="dl_year_stats_csv",
                    )
            with c3:
                disp = papers_df.drop(columns=["tokens"], errors="ignore")
                st.download_button(
                    "corpus_metadata.csv",
                    disp.to_csv(index=False),
                    file_name="corpus_metadata_export.csv",
                    mime="text/csv",
                    key="dl_corpus_csv",
                )
                log_lines = get_activity_log()
                st.download_button(
                    "activity_log.txt",
                    "\n".join(log_lines) if log_lines else "(empty)",
                    file_name="session_activity_log.txt",
                    mime="text/plain",
                    key="dl_log_txt",
                )
            lines = get_activity_log()
            if lines:
                st.code("\n".join(lines[-25:]), language=None)
            if st.button("Clear activity log", key="clear_act_log"):
                from src.app.session_log import clear_activity_log

                clear_activity_log()
                st.rerun()

    if not is_instructor:
        with st.expander("Quick steps (student)", expanded=False):
            st.markdown(
                """
1. **Class collection** — Pick *Browse class collection*; wait for charts if the instructor already loaded papers.  
2. **Practice file** — Pick *Practice file*, upload CSV/JSON (≥5 papers), click *Run NLP*.  
3. **NLP analysis** — Open the second tab for topics, keywords, authors, network, documents, and **Search**.
                """
            )
        _section("How analysis works")
        st.markdown(
            '<div class="ail-shell"><p style="color:#475569;font-size:0.95rem;line-height:1.6;">'
            "The app **cleans** abstracts and titles, finds **themes** (topics), **important words**, **who publishes where**, "
            "and **which papers are related** — then use the **Search** tab on the NLP page to query the corpus in plain language."
            "</p></div>",
            unsafe_allow_html=True,
        )

    return


def _literature_search_response(
    query: str,
    results: dict[str, Any],
    use_chroma_qa: bool,
    store: Any,
    pubmed_url_fn: Callable,
) -> Tuple[str, List[dict]]:
    papers_for_qa = results["papers_df"].drop(columns=["_relevance", "_search_text"], errors="ignore")
    hits_out: List[dict] = []

    if use_chroma_qa and store is not None:
        hits = store.search(query.strip(), n_results=10)
        if not hits:
            return ("No matching papers in the collection for that query.", [])
        for i, hit in enumerate(hits[:10], 1):
            hits_out.append({"type": "chroma", "hit": hit, "rank": i})
    else:
        from src.app.search_qa import search_papers

        ranked, scores = search_papers(query, papers_for_qa, top_k=10)
        if ranked.empty:
            return ("No matching papers for that query.", [])
        for i, (_, row) in enumerate(ranked.head(10).iterrows(), 1):
            sc = scores[i - 1] if i - 1 < len(scores) else 0.0
            hits_out.append({"type": "tfidf", "row": row, "score": sc, "rank": i})

    mode = "**semantic (Chroma)**" if use_chroma_qa and store is not None else "**TF‑IDF**"
    header = f"### Search ({mode})\n\n**{len(hits_out)}** hits.\n\n"

    llm_block = generate_literature_search_answer(query, hits_out)
    if llm_block:
        body = header + llm_block + "\n\n---\n\n" + format_retrieved_documents_markdown(
            hits_out, pubmed_url_fn=pubmed_url_fn, max_docs=10
        )
    else:
        if not USE_LLM_SEARCH_ANSWER:
            header += "_Summary off (AIL_USE_LLM_SEARCH_ANSWER)._\n\n"
        elif not os.getenv("OPENAI_API_KEY", "").strip():
            header += "_No OPENAI_API_KEY — excerpts only._\n\n"
        else:
            header += "_Summary request failed — excerpts only._\n\n"
        body = header + format_retrieved_documents_markdown(
            hits_out, pubmed_url_fn=pubmed_url_fn, max_docs=10
        )

    return (body, hits_out)


def render_nlp_analysis_section(
    results: Optional[dict[str, Any]],
    *,
    source_label: str,
    use_chroma_qa: bool,
    store: Any,
    pubmed_url_fn: Callable,
    document_download_fn: Callable,
    is_instructor: bool = True,
) -> None:
    if is_instructor:
        _hero(
            "NLP analysis workspace",
            "Topic models, bibliometrics, similarity graph, and conversational search over the loaded corpus.",
        )
    else:
        _hero(
            "Explore the literature (NLP)",
            "Use the tabs below to see themes, word trends, who publishes where, how papers connect, and to **Search** the corpus.",
        )

    if results is None:
        if is_instructor:
            st.warning("Load data from the sidebar: PubMed, shared collection, or upload.")
        else:
            st.warning("Choose **Browse class collection** or upload a **practice file** in the sidebar (needs ≥5 papers).")
        return

    st.success(f"**Dataset loaded:** {source_label}")
    if results.get("pipeline_warning"):
        st.warning(results["pipeline_warning"])

    topics_data = results["topics_data"]
    keywords_data = results["keywords_data"]
    keyword_trends = results["keyword_trends"]
    author_stats_df = results["author_stats_df"]
    journal_stats_df = results["journal_stats_df"]
    year_stats_df = results["year_stats_df"]
    cocitation_edges = results["cocitation_edges"]
    papers_df = results["papers_df"]

    tab1, tab2, tab3, tab4, tab5, tab6, tab_qa = st.tabs(
        [
            "Overview",
            "Topics",
            "Keywords",
            "Authors & venues",
            "Similarity map",
            "Paper list",
            "Search",
        ]
    )

    with tab1:
        if not year_stats_df.empty:
            st.bar_chart(year_stats_df.set_index("year"), height=280)
        m1, m2 = st.columns(2)
        m1.metric("Papers", len(papers_df) if not papers_df.empty else 0)
        m2.metric("Topics", len(topics_data))

    with tab2:
        if topics_data:
            html = "<ul style='columns:2;gap:1.5rem;'>"
            for t in topics_data:
                tname = t.get("topic_name") or f"Topic {t.get('topic_id', 0)}"
                docs = int(t.get("documents", 0))
                cites = int(t.get("citation_count", 0))
                html += (
                    f"<li><b>{tname}</b> "
                    f"<span style='opacity:.75'>(docs: {docs}, citations: {cites})</span>: "
                    f"{', '.join(t.get('words', []))}</li>"
                )
            html += "</ul>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("No topics.")

    with tab3:
        if not keyword_trends.empty and "year" in keyword_trends.columns:
            fig_kw = _keyword_strength_trends_figure(
                keyword_trends,
                max_lines=KEYWORD_TREND_CHART_LINES,
                height=560,
            )
            if fig_kw is not None:
                st.plotly_chart(fig_kw, use_container_width=True)
        if keywords_data:
            st.dataframe(pd.DataFrame(keywords_data).head(35), use_container_width=True, height=320)

    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Authors")
            if not author_stats_df.empty:
                st.dataframe(author_stats_df.head(80), use_container_width=True, height=360)
        with c2:
            st.markdown("##### Journals")
            if not journal_stats_df.empty:
                st.dataframe(journal_stats_df.head(80), use_container_width=True, height=360)

    with tab5:
        if not cocitation_edges.empty:
            try:
                import networkx as nx
                import plotly.graph_objects as go

                G = nx.from_pandas_edgelist(cocitation_edges, "source", "target", edge_attr="weight")
                pos = nx.spring_layout(G, k=0.45, iterations=45, seed=42)
                edge_x, edge_y = [], []
                for e in G.edges():
                    x0, y0 = pos[e[0]]
                    x1, y1 = pos[e[1]]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]
                nx_ = [pos[n][0] for n in G.nodes()]
                ny = [pos[n][1] for n in G.nodes()]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=0.4, color="#94a3b8")))
                fig.add_trace(
                    go.Scatter(
                        x=nx_,
                        y=ny,
                        mode="markers",
                        marker=dict(size=7, color="#2563eb"),
                        text=list(G.nodes()),
                        hoverinfo="text",
                    )
                )
                fig.update_layout(showlegend=False, height=480, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as ex:
                st.error(str(ex))
        else:
            st.info("Not enough overlap for a graph — add more papers.")

    with tab6:
        if papers_df.empty:
            st.info("No documents.")
        else:
            clean = papers_df.drop(columns=["_relevance", "_search_text"], errors="ignore")
            dl_label = "Download full table (CSV)" if is_instructor else "Download this table (your session)"
            st.download_button(
                dl_label,
                clean.to_csv(index=False),
                "corpus_export.csv",
                "text/csv",
                key="dl_all",
            )
            pick_label = "Choose a paper" if not is_instructor else "Open document"
            titles = clean["title"].astype(str) if "title" in clean.columns else clean.index.astype(str)
            pick = st.selectbox(pick_label, titles.tolist()[:200])
            row = clean[clean["title"].astype(str) == pick].iloc[0]
            st.markdown(f"### {row.get('title', '')}")
            st.caption(f"{row.get('authors', '')} · {row.get('journal', '')} · {row.get('year', '')}")
            if pd.notna(row.get("abstract")):
                st.write(str(row["abstract"])[:700] + ("…" if len(str(row.get("abstract", ""))) > 700 else ""))
            u = pubmed_url_fn(row.get("pmid"))
            x, y = st.columns(2)
            with x:
                if u:
                    st.link_button("PubMed", u)
            with y:
                st.download_button("Download row", document_download_fn(row), f"doc_{row.get('pmid')}.csv", "text/csv")

    with tab_qa:
        if use_chroma_qa:
            mode = "Meaning-based search (shared collection index)" if not is_instructor else "Semantic search (ChromaDB)"
        else:
            mode = "Keyword relevance (this dataset)" if not is_instructor else "TF‑IDF over corpus"
        st.caption(mode)

        if "qa_chat_messages" not in st.session_state:
            st.session_state["qa_chat_messages"] = []
        for msg in st.session_state["qa_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        ph = "e.g. Which papers discuss readmission risk?"
        prompt = st.chat_input(ph)
        if prompt and prompt.strip():
            st.session_state["qa_chat_messages"].append({"role": "user", "content": prompt.strip()})
            text, meta = _literature_search_response(prompt.strip(), results, use_chroma_qa, store, pubmed_url_fn)
            st.session_state["qa_chat_messages"].append({"role": "assistant", "content": text})
            if is_instructor:
                from src.app.session_log import log_event

                log_event(f"Search: {len(prompt)} chars → {len(meta)} hits")
            st.rerun()
        if st.session_state["qa_chat_messages"] and st.button("Clear search", key="clr_chat"):
            st.session_state["qa_chat_messages"] = []
            st.rerun()
