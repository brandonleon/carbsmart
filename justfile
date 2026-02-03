# Run the FastAPI app locally (default port: 8000).
run port='8000':
  uv run uvicorn app.main:app --reload --port {{port}}

# Build the Docker image.
[group('docker')]
docker-build:
  docker build -t carbsmart .

# Run the Docker image (default host port: 8000).
[group('docker')]
docker-run port='8000':
  mkdir -p data
  docker run --rm -d -p {{port}}:8000 --name carbsmart -v "$(pwd)/data:/app/data" -e DATABASE_URL=sqlite:///./data/carbsmart.db carbsmart
