import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Repo-root .env; does not override existing env.
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

APP_BRAND_NAME = "Clinical Evidence Studio"
APP_TAGLINE = "Research-grade PubMed and NLP workspace for healthcare evidence exploration."
ASSETS_DIR = PROJECT_ROOT / "assets"
APP_LOGO_PATH = ASSETS_DIR / "app_logo.svg"
APP_PAGE_TITLE = f"{APP_BRAND_NAME} · healthcare literature intelligence"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DEMO_DIR = DATA_DIR / "demo"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma"
APP_SQLITE_PATH = DATA_DIR / "app_users.db"
COLLECTION_NAME = "healthcare_papers"
# Large collections: batch writes/reads so Chroma/embeddings stay stable (e.g. 15k+ docs).
CHROMA_UPSERT_BATCH_SIZE = 400
CHROMA_GET_PAGE_SIZE = 2500
# LDA topic count (healthcare literature; needs enough papers — roughly n_topics + 1 documents).
N_TOPICS = 30
KEYWORD_TOP_N = 30
# Keyword trend chart: more lines + richer per-year vocabulary (healthcare corpus).
KEYWORD_TREND_CHART_LINES = 30
KEYWORD_TRENDS_PER_YEAR = 25
COCITATION_MIN_COUNT = 2
COCITATION_TOP_N = 200
DEMO_QUERY = "healthcare machine learning clinical decision support"
DEMO_SIZE = 500
PUBMED_MAX_RETRIEVE_CAP = 100_000
# Default batch size for building a shared Chroma index (~15k papers target; use email + polite pacing per NCBI).
PUBMED_DEFAULT_RETRIEVE = 15_000

PAGE_LITERATURE = "Literature & NLP"
PAGE_ADMIN_DASHBOARD = "Admin dashboard"
PAGE_ADMIN_PERMISSIONS = "Permissions & users"
PAGE_INSTRUCTOR_DASHBOARD = "Instructor dashboard"
PAGE_STUDENT_HOME = "Student home"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# LLM topic labels (needs OPENAI_API_KEY).
# Disabled by default to speed up analysis (~20s saved per run); enable with AIL_USE_LLM_TOPIC_LABELS=1
USE_LLM_TOPIC_LABELS = _env_bool("AIL_USE_LLM_TOPIC_LABELS", False)
LLM_TOPIC_MODEL = os.getenv("AIL_LLM_TOPIC_MODEL", "gpt-4o-mini")
LLM_TOPIC_TIMEOUT_SECONDS = int(os.getenv("AIL_LLM_TOPIC_TIMEOUT_SECONDS", "20"))

# Europe PMC citation counts.
USE_EUROPEPMC_CITATION_ENRICHMENT = _env_bool("AIL_USE_EUROPEPMC_CITATION_ENRICHMENT", True)
EUROPEPMC_CITATION_MAX_LOOKUPS = int(os.getenv("AIL_EUROPEPMC_CITATION_MAX_LOOKUPS", "250"))

# Search tab answer LLM.
USE_LLM_SEARCH_ANSWER = _env_bool("AIL_USE_LLM_SEARCH_ANSWER", True)
LLM_SEARCH_MODEL = os.getenv("AIL_LLM_SEARCH_MODEL", "gpt-4o-mini")
LLM_SEARCH_TIMEOUT_SECONDS = int(os.getenv("AIL_LLM_SEARCH_TIMEOUT_SECONDS", "45"))
