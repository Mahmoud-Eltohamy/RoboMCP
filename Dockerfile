FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxkbcommon0 \
    libwayland-client0 \
    libnss3 \
    libnspr4 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY pyproject.toml /app/
COPY setup.py /app/
COPY uv.lock /app/

# Install required packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir setuptools wheel && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir ollama playwright && \
    playwright install chromium

# Copy the application code
COPY . /app/

# Expose ports for the MCP server and browser debugging
EXPOSE 5000
EXPOSE 9222

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV BROWSER_WS_ENDPOINT=ws://localhost:9222

# Run the MCP Appium server
CMD ["python", "main.py", "--server"]