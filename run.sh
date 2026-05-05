#!/usr/bin/env bash
# Run AI Literacy project end-to-end (synthetic demo data).
# Usage: ./run.sh   or   bash run.sh
set -e
cd "$(dirname "$0")"

echo "=== 1. Generate demo data (synthetic) ==="
python scripts/generate_demo_csv.py

echo "=== 2. Run pipeline ==="
python scripts/run_pipeline.py

echo "=== 3. Start Streamlit app ==="
echo "Open http://localhost:8501 in your browser."
exec streamlit run src/app/main.py --server.port=8501
