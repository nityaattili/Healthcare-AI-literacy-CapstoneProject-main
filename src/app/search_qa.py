import re
from typing import List, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def search_papers(query: str, df: pd.DataFrame, text_cols=("title", "abstract"), top_k: int = 15):
    if df.empty:
        return pd.DataFrame(), []
    texts = []
    for _, row in df.iterrows():
        parts = [str(row.get(c, "")) for c in text_cols if c in df.columns]
        texts.append(" ".join(parts))
    vec = TfidfVectorizer(max_features=5000, stop_words="english")
    try:
        X = vec.fit_transform(texts)
        q = vec.transform([query])
        import numpy as np

        scores = (X @ q.T).toarray().ravel()
    except ValueError:
        return pd.DataFrame(), []
    idx = scores.argsort()[::-1][:top_k]
    idx = [i for i in idx if scores[i] > 0]
    if not idx:
        return pd.DataFrame(), []
    return df.iloc[idx], [float(scores[i]) for i in idx]


def snippet(text: str, query: str, max_len: int = 280) -> str:
    t = re.sub(r"\s+", " ", str(text))[:2000]
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"
