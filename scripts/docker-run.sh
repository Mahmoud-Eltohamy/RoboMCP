#!/bin/bash

# Script to help setting up and running the Docker environment for MCP Appium

# Default values
ACTION="up"
DETACHED=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --build)
      ACTION="build"
      shift
      ;;
    --up)
      ACTION="up"
      shift
      ;;
    --down)
      ACTION="down"
      shift
      ;;
    --restart)
      ACTION="restart"
      shift
      ;;
    --detached|-d)
      DETACHED=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --build              Build the Docker images"
      echo "  --up                 Start the Docker containers (default)"
      echo "  --down               Stop and remove the Docker containers"
      echo "  --restart            Restart the Docker containers"
      echo "  --detached, -d       Run containers in detached mode"
      echo "  --help, -h           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Load environment variables from .env.docker file
echo "Loading environment variables from .env.docker..."
export $(grep -v '^#' .env.docker | xargs)

# Execute the appropriate Docker Compose command
case $ACTION in
  "build")
    echo "Building Docker images..."
    docker-compose build
    ;;
  "up")
    echo "Starting Docker containers..."
    if [ "$DETACHED" = true ]; then
      docker-compose up -d
      echo "Containers are running in the background. Use 'docker-compose logs -f' to see logs."
    else
      docker-compose up
    fi
    ;;
  "down")
    echo "Stopping and removing Docker containers..."
    docker-compose down
    ;;
  "restart")
    echo "Restarting Docker containers..."
    docker-compose restart
    ;;
esac

# Display info if containers are starting
if [ "$ACTION" = "up" ] || [ "$ACTION" = "restart" ]; then
    echo ""
    echo "Access Information:"
    echo "- Android Emulator Web Interface: http://localhost:6080"
    echo "- MCP Appium Web Interface: http://localhost:5000"
    echo ""
    
    if [ "$DETACHED" = true ]; then
        echo "To run the Android example:"
        echo "docker exec -it mcp-appium python examples/android_example.py"
        echo ""
        echo "To run the Sauce Labs Demo App example:"
        echo "docker exec -it mcp-appium python examples/docker_sauce_labs_example.py"
        echo ""
    fi
fi