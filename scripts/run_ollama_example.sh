#!/bin/bash
# Script to run the Ollama integration example

set -e  # Exit on error

# Check if the Ollama example script exists
if [ ! -f "examples/ollama_example.py" ]; then
    echo "Error: examples/ollama_example.py not found!"
    exit 1
fi

# Ensure script is executable
chmod +x examples/ollama_example.py

# Set default values
OLLAMA_HOST=${OLLAMA_BASE_URL:-"http://localhost:11434"}
MODEL=${OLLAMA_MODEL:-"mistral:7b-instruct"}
TEMPERATURE=${OLLAMA_TEMPERATURE:-0.7}
MAX_TOKENS=${OLLAMA_MAX_TOKENS:-1024}

# Run the example
echo "Running Ollama integration example..."
echo "Host: $OLLAMA_HOST"
echo "Model: $MODEL"
echo "Temperature: $TEMPERATURE"
echo "Max Tokens: $MAX_TOKENS"
echo ""

python examples/ollama_example.py \
  --ollama-host "$OLLAMA_HOST" \
  --model "$MODEL" \
  --temperature "$TEMPERATURE" \
  --max-tokens "$MAX_TOKENS"

echo ""
echo "Example completed."
