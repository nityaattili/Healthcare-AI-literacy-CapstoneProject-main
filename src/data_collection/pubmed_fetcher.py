import xml.etree.ElementTree as ET
from typing import List, Optional

import pandas as pd

try:
    from Bio import Entrez
except ImportError:
    Entrez = None


def _parse_pubmed_article(article) -> Optional[dict]:
    try:
        med = article.find(".//MedlineCitation")
        if med is None:
            return None
        pmid_el = med.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        art = med.find("Article")
        if art is None:
            return None
        title_el = art.find("ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""
        abs_el = art.find("Abstract")
        abstract = ""
        if abs_el is not None:
            abstract = " ".join("".join(a.itertext()) for a in abs_el.findall("AbstractText"))
        journal = ""
        j = art.find("Journal/Title")
        if j is not None and j.text:
            journal = j.text
        year = None
        y = art.find(".//PubDate/Year")
        if y is not None and y.text:
            try:
                year = int(y.text)
            except ValueError:
                pass
        authors = []
        for au in art.findall("AuthorList/Author"):
            ln = au.find("LastName")
            fn = au.find("ForeName")
            if ln is not None:
                authors.append(f"{ln.text or ''} {fn.text if fn is not None else ''}".strip())
        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": "; ".join(authors),
            "journal": journal,
            "year": year,
            "keywords": "",
        }
    except Exception:
        return None


def fetch_pubmed_batch(
    query: str,
    max_results: int = 100,
    email: Optional[str] = None,
    batch_size: int = 200,
) -> pd.DataFrame:
    if Entrez is None:
        raise RuntimeError("Biopython required for PubMed")
    if email:
        Entrez.email = email
    else:
        Entrez.email = "literature.portal@local"
    esearch_page_max = 10_000
    ids: List[str] = []
    retstart = 0
    while len(ids) < max_results:
        need = max_results - len(ids)
        retmax = min(esearch_page_max, need)
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=retmax,
            retstart=retstart,
            sort="relevance",
        )
        record = Entrez.read(handle)
        handle.close()
        page_ids: List[str] = record.get("IdList", [])
        if not page_ids:
            break
        ids.extend(page_ids)
        retstart += len(page_ids)
        if len(page_ids) < retmax:
            break
    ids = ids[:max_results]
    if not ids:
        return pd.DataFrame()
    rows = []
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i : i + batch_size]
        h2 = Entrez.efetch(db="pubmed", id=batch_ids, rettype="xml", retmode="xml")
        xml_txt = h2.read()
        h2.close()
        root = ET.fromstring(xml_txt)
        for art in root.findall(".//PubmedArticle"):
            r = _parse_pubmed_article(art)
            if r:
                rows.append(r)
    return pd.DataFrame(rows)


def fetch_pubmed_papers(query: str, max_results: int = 100, out_path: Optional[str] = None, email: Optional[str] = None) -> pd.DataFrame:
    df = fetch_pubmed_batch(query, max_results=max_results, email=email)
    if out_path:
        df.to_csv(out_path, index=False)
    return df
