run port='8000':
  uv run uvicorn app.main:app --reload --port {{port}}

docker-build:
  docker build -t carbsmart .

docker-run port='8000':
  mkdir -p data
  docker run --rm -p {{port}}:8000 -v "$(pwd)/data:/app/data" -e DATABASE_URL=sqlite:///./data/carbsmart.db carbsmart
