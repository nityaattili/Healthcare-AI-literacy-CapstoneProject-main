import pandas as pd


def get_full_sample_df() -> pd.DataFrame:
    rows = []
    for i in range(25):
        rows.append(
            {
                "pmid": str(100000 + i),
                "title": f"Sample paper {i+1}: predictive models in hospital workflows",
                "abstract": "Background: Predictive models are increasingly used in clinical workflows. "
                "Methods: We summarize cohort studies and validation practice. Results: Performance varies by setting. "
                "Conclusion: External validation and monitoring remain essential.",
                "authors": "Doe, Jane; Smith, Alex",
                "journal": "J Med Inform",
                "year": 2020 + (i % 5),
                "keywords": "machine learning; clinical informatics; cohort study",
            }
        )
    return pd.DataFrame(rows)
