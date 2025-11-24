FROM python:3.10-slim

# 1. Install system dependencies
# We need curl/build-essential for some system-level compile tasks if wheels aren't available
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    neovim \
    && rm -rf /var/lib/apt/lists/*

# 2. Install uv
# We copy the pre-compiled binary from the official image (super fast)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Setup Workdir
WORKDIR /app

# 4. Copy dependencies
COPY requirements.txt .

# 5. Install dependencies using uv
# --system flag tells uv to install into the global Python environment 
# (which is fine since we are inside a container)
RUN uv pip install --system --no-cache -r requirements.txt

# 6. Copy application code
COPY app.py .
COPY ./assets/ ./assets/

# 7. Expose Port
EXPOSE 8501

# 8. Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 9. Entrypoint
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]