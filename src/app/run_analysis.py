import json
from urllib.request import Request, urlopen
import pandas as pd

from config.settings import (
    COCITATION_MIN_COUNT,
    COCITATION_TOP_N,
    KEYWORD_TOP_N,
    KEYWORD_TRENDS_PER_YEAR,
    N_TOPICS,
    USE_LLM_TOPIC_LABELS,
    USE_EUROPEPMC_CITATION_ENRICHMENT,
    EUROPEPMC_CITATION_MAX_LOOKUPS,
)
from src.analytics.author_stats import author_stats, journal_stats, year_stats
from src.analytics.cocitation import build_cocitation_edges
from src.nlp.keyword_extraction import extract_keywords, keyword_trends_over_time
from src.nlp.topic_model import fit_lda, get_topic_summary
from src.preprocessing.text_cleaner import preprocess_corpus
import hashlib
import pickle
from pathlib import Path
from config.settings import PROJECT_ROOT

# Add a cache salt so citation/enrichment changes invalidate old cache
CACHE_SALT = f"cit_v2_enrich_{'1' if USE_EUROPEPMC_CITATION_ENRICHMENT else '0'}"


def _pick_citation_series(df: pd.DataFrame) -> pd.Series | None:
    """Return a citation-count series if present under common names; else None."""
    for col in [
        "citation_count",
        "citations",
        "n_citations",
        "times_cited",
        "cited_by",
        "citedby",
    ]:
        if col in df.columns:
            return df[col].fillna(0)
    return None


def _fetch_europepmc_citations(pmids: list[str], *, cap: int) -> dict[str, int]:
    """Fetch citedByCount from Europe PMC for a list of PMIDs (best-effort, capped)."""
    out: dict[str, int] = {}
    n = 0
    for pmid in pmids:
        if not pmid or n >= cap:
            break
        try:
            url = (
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                f"?query=EXT_ID:{pmid}%20AND%20SRC:MED&resultType=core&format=json"
            )
            req = Request(url, headers={"User-Agent": "AILiteracy/1.0"}, method="GET")
            with urlopen(req, timeout=10) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            rs = (payload.get("resultList") or {}).get("result") or []
            if rs:
                c = int(rs[0].get("citedByCount") or 0)
                if c > 0:
                    out[pmid] = c
        except Exception:
            # Ignore individual lookup failures
            pass
        n += 1
    return out


def run_pipeline_on_dataframe(df: pd.DataFrame) -> dict:
    if len(df) < 2:
        return _empty_results(df)
    # Best-effort cache: avoid recomputing pipeline for identical inputs
    cache_file = None
    try:
        cache_dir = Path(PROJECT_ROOT) / "output" / "pipeline_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        # Include salt and first 100 PMIDs (if present) to reduce stale caches when citation logic changes
        pmid_part = ""
        try:
            if "pmid" in df.columns:
                pmid_part = "\n" + "|".join(str(x) for x in df["pmid"].astype(str).head(100).tolist())
        except Exception:
            pmid_part = ""
        key_src = CACHE_SALT + "\n" + df.to_csv(index=False) + pmid_part
        key = hashlib.sha256(key_src.encode("utf-8")).hexdigest()
        cache_file = cache_dir / f"pipeline_{key}.pkl"
        if cache_file.is_file():
            try:
                with cache_file.open("rb") as f:
                    cached = pickle.load(f)
                    return cached
            except Exception:
                # ignore cache read errors and recompute
                pass
    except Exception:
        cache_file = None

    proc = preprocess_corpus(df)
    topics_data = []
    pipeline_warning: str | None = None
    try:
        # Determine valid-token rows to keep mapping between LDA docs and original rows
        valid_mask = proc["tokens"].apply(lambda xs: isinstance(xs, list) and len(xs) > 0)
        tokens_nonempty = proc.loc[valid_mask, "tokens"]
        valid_idx = list(tokens_nonempty.index)

        # Cap by corpus size: LDA needs fewer topics than documents (gensim/fit_lda also enforce this).
        lda, _dictionary, _corpus = fit_lda(
            tokens_nonempty,
            num_topics=min(N_TOPICS, max(2, len(tokens_nonempty) - 1)),
        )
        topics_data = get_topic_summary(lda, top_n=12)

        # Calculate dominant topic per valid document
        from src.nlp.topic_model import get_document_topics
        doc_topics = get_document_topics(lda, _corpus)
        dominant: list[int] = []
        for tps in doc_topics:
            if tps:
                dominant.append(max(tps, key=lambda x: x[1])[0])
            else:
                dominant.append(-1)

        # Count documents per topic
        topic_doc_counts = {i: 0 for i in range(lda.num_topics)}
        for t_id in dominant:
            if t_id >= 0:
                topic_doc_counts[t_id] += 1
        for t in topics_data:
            t["documents"] = topic_doc_counts.get(t["topic_id"], 0)

        # Compute citation_count per topic from data if present; else try Europe PMC
        cites_series = _pick_citation_series(proc)
        cites_by_row: dict[int, int] = {}
        if cites_series is not None:
            for i, v in cites_series.items():
                try:
                    cites_by_row[i] = int(v)
                except Exception:
                    cites_by_row[i] = 0
        elif USE_EUROPEPMC_CITATION_ENRICHMENT and "pmid" in proc.columns:
            # Best-effort enrichment using valid rows only
            pmids = [str(proc.at[i, "pmid"]).strip() if not pd.isna(proc.at[i, "pmid"]) else "" for i in valid_idx]
            pmids = [p for p in pmids if p.isdigit()]
            mp = _fetch_europepmc_citations(pmids[:EUROPEPMC_CITATION_MAX_LOOKUPS], cap=EUROPEPMC_CITATION_MAX_LOOKUPS)
            for i in valid_idx:
                p = str(proc.at[i, "pmid"]).strip() if "pmid" in proc.columns else ""
                cites_by_row[i] = int(mp.get(p, 0)) if p else 0
        else:
            cites_by_row = {i: 0 for i in valid_idx}

        # Sum citations per topic (valid rows only)
        topic_cite_counts = {i: 0 for i in range(lda.num_topics)}
        for row_pos, row_idx in enumerate(valid_idx):
            t_id = dominant[row_pos] if row_pos < len(dominant) else -1
            if t_id >= 0:
                topic_cite_counts[t_id] += int(cites_by_row.get(row_idx, 0))
        for t in topics_data:
            t["citation_count"] = int(topic_cite_counts.get(t["topic_id"], 0))

        # Optional: Apply LLM topic names if enabled and OpenAI API is available (latency tradeoff)
        if USE_LLM_TOPIC_LABELS:
            try:
                import os
                if os.getenv("OPENAI_API_KEY", "").strip():
                    from src.nlp.llm_topic_labeller import apply_llm_topic_names
                    topics_data = apply_llm_topic_names(topics_data, proc)
            except Exception:
                pass
    except ValueError as ex:
        pipeline_warning = str(ex)
    keywords_data = extract_keywords(proc["cleaned_text"], top_n=KEYWORD_TOP_N)
    keyword_trends = keyword_trends_over_time(proc, top_per_year=KEYWORD_TRENDS_PER_YEAR)
    author_stats_df = author_stats(proc)
    journal_stats_df = journal_stats(proc)
    year_stats_df = year_stats(proc)
    edges = build_cocitation_edges(
        proc,
        min_cooccur=COCITATION_MIN_COUNT,
        top_n_edges=COCITATION_TOP_N,
    )
    cocitation_edges = pd.DataFrame(edges, columns=["source", "target", "weight"]) if edges else pd.DataFrame()
    result = {
        "topics_data": topics_data,
        "keywords_data": keywords_data,
        "keyword_trends": keyword_trends,
        "author_stats_df": author_stats_df,
        "journal_stats_df": journal_stats_df,
        "year_stats_df": year_stats_df,
        "cocitation_edges": cocitation_edges,
        "papers_df": proc,
        "pipeline_warning": pipeline_warning,
    }
    # Write cache (best-effort)
    try:
        if cache_file is not None:
            with cache_file.open("wb") as f:
                pickle.dump(result, f)
    except Exception:
        pass
    return result


def _empty_results(df: pd.DataFrame) -> dict:
    return {
        "topics_data": [],
        "keywords_data": [],
        "keyword_trends": pd.DataFrame(),
        "author_stats_df": pd.DataFrame(),
        "journal_stats_df": pd.DataFrame(),
        "year_stats_df": pd.DataFrame(),
        "cocitation_edges": pd.DataFrame(),
        "papers_df": df,
        "pipeline_warning": None,
    }
