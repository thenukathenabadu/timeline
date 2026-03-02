FROM python:3.11-slim

WORKDIR /app

# System deps for asyncpg (libpq) and sentence-transformers (build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install torch CPU-only first (avoids downloading the 2 GB CUDA build)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install everything else
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
