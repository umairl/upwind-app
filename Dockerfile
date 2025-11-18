FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all service directories with their structure
COPY suggestion/ /app/suggestion/
COPY related/ /app/related/
COPY multiagent/ /app/multiagent/

# Create virtual environment and install dependencies for suggestion service
RUN cd /app/suggestion && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create virtual environment and install dependencies for related service
RUN cd /app/related && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create virtual environment and install dependencies for multiagent service
RUN cd /app/multiagent && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose all ports
EXPOSE 8000 8001 8002

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]