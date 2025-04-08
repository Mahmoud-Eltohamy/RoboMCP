# Docker Setup for MCP Appium

This guide explains how to use Docker to set up a complete environment for running the MCP Appium implementation, including an Appium server and Android emulator.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Basic understanding of Docker concepts

## Components

The Docker setup consists of three main components:

1. **Appium Server** - A container running the Appium server
2. **Android Emulator** - A container with an Android emulator 
3. **MCP Appium** - Your application that connects to the Appium server

## Running the Environment

### 1. Start the Docker Containers

```bash
docker-compose up
```

### 2. Access the Android Emulator

The Android emulator can be accessed via a VNC viewer or browser:

- **Web Access**: Open http://localhost:6080 in your browser
- **VNC Access**: Connect to localhost:5901 using a VNC client (password: `secret`)

### 3. Running Tests

Once the environment is up and running, you can run tests against the emulator:

```bash
# Inside the MCP Appium container
docker exec -it mcp-appium python examples/android_example.py
```

## Configuration

### Environment Variables

You can configure the Docker setup using environment variables:

- `APPIUM_URL`: URL of the Appium server (default: `http://appium:4723`)
- `MCP_PORT`: Port for the MCP server (default: `5000`)
- `MCP_LOG_LEVEL`: Logging level for MCP (default: `INFO`)
- `ANDROID_APP_PATH`: Path to the Android app to test (default: uses Android Settings app)

### Adding Your Own Apps

To test with your own Android apps:

1. Place your `.apk` file in the `app/` directory
2. Set the `ANDROID_APP_PATH` environment variable:

```bash
ANDROID_APP_PATH=/app/your-app.apk docker-compose up
```

## Troubleshooting

### Appium Server Connection Issues

If the MCP server cannot connect to the Appium server:

```bash
# Check if the Appium server is running
docker logs appium-server

# Make sure the network is properly configured
docker network inspect appium-network
```

### Android Emulator Issues

If the Android emulator doesn't start properly:

```bash
# Check the emulator logs
docker logs android-emulator

# Access the emulator via VNC to see what's happening
# Use a VNC client to connect to localhost:5901
```

### MCP Server Issues

If the MCP server has problems:

```bash
# Check the MCP server logs
docker logs mcp-appium

# Access the MCP server shell
docker exec -it mcp-appium bash
```

## Advanced Usage

### Customizing the Android Device

You can customize the Android device by modifying the environment variables in the `docker-compose.yml` file:

```yaml
environment:
  - DEVICE=Samsung Galaxy S10  # Change to a different device
```

### Persistent Data

The Docker Compose configuration maps the `./app` and `./data` directories to the containers, so your apps and test data are preserved between container restarts.