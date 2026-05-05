import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from gensim import corpora, models


def fit_lda(
    token_series: pd.Series,
    num_topics: int = 30,
    passes: int = 10,
) -> Tuple[models.LdaModel, corpora.Dictionary, List]:
    texts: List[List[str]] = []
    for raw in token_series.tolist():
        if raw is None:
            continue
        row = list(raw) if not isinstance(raw, list) else raw
        if row:
            texts.append(row)

    if not texts:
        raise ValueError(
            "No tokens left for topic modeling. Check that title/abstract columns have real English text. "
            "On a fresh machine NLTK needs a one-time download of punkt and stopwords (run with internet once)."
        )

    dictionary = corpora.Dictionary(texts)
    n_docs = len(texts)
    no_below = 2 if n_docs >= 15 else 1
    no_above = 0.9 if n_docs < 25 else 0.85
    dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=5000)

    if len(dictionary) == 0:
        dictionary = corpora.Dictionary(texts)
        dictionary.filter_extremes(no_below=1, no_above=1.0, keep_n=5000)

    if len(dictionary) == 0:
        raise ValueError(
            "LDA vocabulary is empty (often too few papers or words that never repeat). "
            "Try more rows, longer abstracts, or at least ~10–15 documents."
        )

    corpus = [dictionary.doc2bow(t) for t in texts]
    token_total = sum(cnt for bow in corpus for _, cnt in bow)
    if token_total == 0:
        raise ValueError("LDA input has zero counts after building the document-term matrix.")

    nt = min(max(2, num_topics), max(2, n_docs - 1), max(2, len(dictionary)))
    passes_use = min(passes, 5) if n_docs < 12 else passes

    lda = models.LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=nt,
        passes=passes_use,
        alpha="auto",
        eta="auto",
        random_state=42,
    )
    return lda, dictionary, corpus


def get_topic_summary(lda: models.LdaModel, top_n: int = 10) -> List[Dict[str, Any]]:
    out = []
    for i in range(lda.num_topics):
        words = [w for w, _ in lda.show_topic(i, topn=top_n)]
        # Generate a default topic name from top 3 words (title case)
        default_name = " / ".join([w.title() for w in words[:3]]) if words else f"Topic {i}"
        out.append({
            "topic_id": i, 
            "words": words,
            "topic_name": default_name,  # Default name from top words; can be overridden by LLM
            "documents": 0,  # Will be calculated when needed
            "citation_count": 0  # Placeholder for citation data (not available in raw LDA output)
        })
    return out


def get_document_topics(lda: models.LdaModel, corpus: List) -> List[List[Tuple[int, float]]]:
    return [list(lda.get_document_topics(bow, minimum_probability=0.01)) for bow in corpus]


def save_lda(lda: models.LdaModel, dictionary: corpora.Dictionary, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    lda.save(str(out_dir / "lda.model"))
    dictionary.save(str(out_dir / "lda.dict"))


def load_lda(model_dir: Path) -> Tuple[models.LdaModel, corpora.Dictionary]:
    lda = models.LdaModel.load(str(model_dir / "lda.model"))
    dictionary = corpora.Dictionary.load(str(model_dir / "lda.dict"))
    return lda, dictionary
