#!/bin/bash

# Run the MCP Appium MCP Protocol Example

# Check for the --server flag
if [ "$1" == "--server" ]; then
  # Start the MCP server in background
  echo "Starting MCP server..."
  python main.py --server &
  SERVER_PID=$!
  echo "MCP server started with PID $SERVER_PID"
  
  # Wait for server to initialize
  echo "Waiting for server to initialize..."
  sleep 5
fi

# Run the MCP example
echo "Running MCP example..."
python examples/mcp_example.py

# If we started the server, stop it
if [ ! -z ${SERVER_PID+x} ]; then
  echo "Stopping MCP server..."
  kill $SERVER_PID
fi
