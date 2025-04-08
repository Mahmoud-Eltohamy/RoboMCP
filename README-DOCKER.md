# Docker Setup for MCP Appium

This document explains how to use the Docker setup for MCP Appium.

## Quick Start

```bash
# Start the Docker environment
./scripts/docker-run.sh

# Build images first if needed
./scripts/docker-run.sh --build

# Run in detached mode
./scripts/docker-run.sh -d
```

## What's Included

The Docker setup includes:

1. **Appium Server**: A containerized Appium server ready to connect to mobile devices or emulators.
2. **Android Emulator**: A preconfigured Android emulator with VNC access.
3. **MCP Appium Server**: Your application running in a container and connected to the Appium server.

## Accessing Components

- **Android Emulator UI**: http://localhost:6080 in your browser
- **MCP Appium Web Interface**: http://localhost:5000

## Running Tests

With the Docker environment running, you can execute the example tests:

```bash
# Run the Android example
docker exec -it mcp-appium python examples/android_example.py

# Run the iOS example (requires additional setup)
docker exec -it mcp-appium python examples/ios_example.py
```

## Configuration

You can configure the environment by editing the `.env.docker` file or by setting environment variables before running the Docker containers.

## Important Files

- `docker-compose.yml`: Defines the Docker services
- `.env.docker`: Environment variable configuration
- `Dockerfile`: Instructions for building the MCP Appium image
- `docker-run.sh`: Helper script for managing the Docker environment

## Troubleshooting

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Make sure the Android emulator is fully started before running tests (check VNC viewer)
3. Verify network connectivity between containers: `docker network inspect appium-network`

For more advanced troubleshooting, see the [DOCKER.md](./DOCKER.md) file.