#!/bin/bash

# 1. Start the Ollama server in the background
/bin/ollama serve &

# Record the Process ID (PID) to wait for it later
pid=$!

# 2. Wait a few seconds for the server to wake up
sleep 5

# 3. Check if 'llama3' is installed. If not, pull it.
echo "🔴 Checking for llama 3 8B model..."
if ! ollama list | grep -q "llama3"; then
  echo "⚙️  Model not found. Pulling qwen now..."
  ollama pull llama3:8b
  echo "✅ Model pulled successfully!"
else
  echo "✅ Llama 3 8B is already installed."
fi

# 4. Wait for the background process (keep the container alive)
wait $pid