# AI Literacy – Clinical Literature Analysis
FROM python:3.11-slim

WORKDIR /app

# Install system deps for building wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt')"

# Optional: small spaCy model (uncomment if using spacy in pipeline)
# RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

COPY config/ config/
COPY src/ src/
COPY scripts/ scripts/

# Create data and output dirs
RUN mkdir -p data/demo output

# Default: run streamlit (assume pre-built output or mount volume)
ENV STREAMLIT_SERVER_HEADLESS=true
EXPOSE 8501
CMD ["streamlit", "run", "src/app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
