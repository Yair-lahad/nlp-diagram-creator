FROM python:3.12-slim

WORKDIR /app

# Install Graphviz (required for diagrams package)
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]