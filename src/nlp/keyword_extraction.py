from typing import List, Tuple

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def extract_keywords(
    texts: pd.Series,
    top_n: int = 30,
    use_tfidf: bool = True,
    min_df: int = 2,
    max_df: float = 0.85,
) -> List[dict]:
    docs = texts.fillna("").astype(str).tolist()
    n = len(docs)
    if n == 0:
        return []

    use_min_df = 1 if n < 6 else min_df
    use_max_df: float | int = 1.0 if n < 8 else max_df

    def _fit(vec_cls):
        vec = vec_cls(
            max_features=5000,
            min_df=use_min_df,
            max_df=use_max_df,
            stop_words="english",
        )
        return vec, vec.fit_transform(docs)

    try:
        if use_tfidf:
            vec, X = _fit(TfidfVectorizer)
        else:
            vec, X = _fit(CountVectorizer)
    except ValueError:
        use_min_df, use_max_df = 1, 1.0
        try:
            if use_tfidf:
                vec, X = _fit(TfidfVectorizer)
            else:
                vec, X = _fit(CountVectorizer)
        except ValueError:
            return []

    if X.shape[1] == 0:
        return []
    scores = X.sum(axis=0).A1
    terms = vec.get_feature_names_out()
    idx = scores.argsort()[::-1][:top_n]
    return [{"keyword": terms[i], "score": float(scores[i])} for i in idx]


def keyword_trends_over_time(
    df: pd.DataFrame,
    text_col: str = "cleaned_text",
    year_col: str = "year",
    top_per_year: int = 8,
) -> pd.DataFrame:
    if year_col not in df.columns or text_col not in df.columns:
        return pd.DataFrame(columns=["year", "keyword", "score"])
    rows = []
    df = df.copy()
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    for year, g in df.dropna(subset=[year_col]).groupby(year_col):
        if g.empty:
            continue
        kws = extract_keywords(g[text_col], top_n=top_per_year)
        for k in kws:
            rows.append({"year": int(year), "keyword": k["keyword"], "score": k["score"]})
    return pd.DataFrame(rows)
