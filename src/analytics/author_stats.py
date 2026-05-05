import pandas as pd


def _split_authors(authors_str: str) -> list:
    if pd.isna(authors_str) or not str(authors_str).strip():
        return []
    s = str(authors_str).strip()
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]
    return [x.strip() for x in s.split(",") if x.strip()]


def author_stats(df: pd.DataFrame, authors_column: str = "authors", top_n: int = 50) -> pd.DataFrame:
    if authors_column not in df.columns:
        return pd.DataFrame(columns=["author", "count"])
    all_authors = []
    for val in df[authors_column].fillna(""):
        all_authors.extend(_split_authors(val))
    counts = pd.Series(all_authors).value_counts()
    out = counts.head(top_n).reset_index()
    out.columns = ["author", "count"]
    return out


def journal_stats(df: pd.DataFrame, journal_column: str = "journal", top_n: int = 50) -> pd.DataFrame:
    if journal_column not in df.columns:
        return pd.DataFrame(columns=["journal", "count"])
    counts = df[journal_column].fillna("(Unknown)").value_counts()
    out = counts.head(top_n).reset_index()
    out.columns = ["journal", "count"]
    return out


def year_stats(df: pd.DataFrame, year_column: str = "year") -> pd.DataFrame:
    if year_column not in df.columns:
        return pd.DataFrame(columns=["year", "count"])
    d = df.copy()
    d[year_column] = pd.to_numeric(d[year_column], errors="coerce")
    counts = d.dropna(subset=[year_column]).groupby(year_column).size().reset_index(name="count")
    counts.columns = ["year", "count"]
    return counts.sort_values("year")
