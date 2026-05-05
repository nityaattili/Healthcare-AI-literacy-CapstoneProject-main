import re
from typing import List

import nltk
import pandas as pd

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)
try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_stop = set(stopwords.words("english"))
_lemma = WordNetLemmatizer()


def clean_text(text: str, min_len: int = 2) -> List[str]:
    if not text or not str(text).strip():
        return []
    s = str(text).lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    tokens = word_tokenize(s)
    out = []
    for t in tokens:
        if len(t) < min_len or t in _stop:
            continue
        out.append(_lemma.lemmatize(t))
    return out


def preprocess_corpus(df: pd.DataFrame, text_cols=("title", "abstract")) -> pd.DataFrame:
    df = df.copy()
    parts = []
    for c in text_cols:
        if c in df.columns:
            parts.append(df[c].fillna("").astype(str))
        else:
            parts.append(pd.Series([""] * len(df)))
    combined = parts[0]
    for p in parts[1:]:
        combined = combined + " " + p
    df["tokens"] = combined.apply(clean_text)
    df["cleaned_text"] = df["tokens"].apply(lambda xs: " ".join(xs))
    return df
