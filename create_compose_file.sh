#!/bin/bash

# Script to generate docker-compose.yml based on OLLAMA_ACCELERATION value in .env

set -e

ENV_FILE=".env"
OUTPUT_FILE="compose.yml"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE file not found!"
    exit 1
fi

# Read OLLAMA_ACCELERATION from .env file
source "$ENV_FILE"

# Validate OLLAMA_ACCELERATION variable
if [ -z "$OLLAMA_ACCELERATION" ]; then
    echo "Error: OLLAMA_ACCELERATION not set in $ENV_FILE"
    exit 1
fi

if [ "$OLLAMA_ACCELERATION" != "cpu" ] && [ "$OLLAMA_ACCELERATION" != "gpu" ]; then
    echo "Error: OLLAMA_ACCELERATION must be either 'cpu' or 'gpu', got: $OLLAMA_ACCELERATION"
    exit 1
fi

echo "Generating $OUTPUT_FILE with OLLAMA_ACCELERATION=$OLLAMA_ACCELERATION..."

# Generate the docker-compose.yml file
cat > "$OUTPUT_FILE" << 'EOF'
services:
  # 1. AI Backend
  ollama:
    build:
      context: .
      dockerfile: Dockerfile.ollama
    container_name: ollama_backend
    ports:
      - "11434:11434"
    volumes:
      - ollama_storage:/root/.ollama

  # 2. Streamlit App (Internal Only)
  streamlit-app:
EOF

# Add conditional build configuration based on OLLAMA_ACCELERATION
if [ "$OLLAMA_ACCELERATION" = "gpu" ]; then
    cat >> "$OUTPUT_FILE" << 'EOF'
    build:
      context: .
      dockerfile: Dockerfile_gpu
    container_name: json_rag_ui
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
EOF
else
    cat >> "$OUTPUT_FILE" << 'EOF'
    build:
      context: .
      dockerfile: Dockerfile
    container_name: json_rag_ui
EOF
fi

# Add the common configuration for streamlit-app
cat >> "$OUTPUT_FILE" << 'EOF'
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./data:/app/data
      - index_volume:/app/index_storage

  # 3. Nginx Reverse Proxy
  nginx:
    build: ./nginx
    container_name: nginx_proxy
    ports:
      - "443:443"
      - "80:80"
    depends_on:
      - streamlit-app

volumes:
  ollama_storage:
  index_volume:
EOF

echo "✓ Successfully generated $OUTPUT_FILE for $OLLAMA_ACCELERATION mode"
