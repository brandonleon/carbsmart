run:
  uv run uvicorn app.main:app --reload

docker-build:
  docker build -t carbsmart .

docker-run:
  mkdir -p data
  docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" -e DATABASE_URL=sqlite:///./data/carbsmart.db carbsmart
