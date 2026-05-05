import io
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

EXPECTED = ["title", "abstract", "authors", "journal", "year", "pmid", "keywords"]


def _normalize_papers_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    colmap = {c.lower().strip(): c for c in df.columns}
    for want in EXPECTED:
        low = want.lower()
        if low in colmap and want not in df.columns:
            df[want] = df[colmap[low]]
    if "pmid" not in df.columns and "id" in df.columns:
        df["pmid"] = df["id"]
    for c in EXPECTED:
        if c not in df.columns:
            df[c] = "" if c != "year" else None
    return df


def load_papers(path: Union[str, Path]) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_json(path)
    return _normalize_papers_df(df)


def load_papers_from_bytes(data: bytes, filename: str) -> pd.DataFrame:
    name = filename.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(data))
    else:
        df = pd.read_json(io.BytesIO(data))
    return _normalize_papers_df(df)


def save_papers(df: pd.DataFrame, path: Union[str, Path]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
    else:
        df.to_json(path, orient="records", indent=2)
