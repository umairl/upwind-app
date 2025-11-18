FROM python:3.9-slim

# Set working dir
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application folders
COPY suggestion/ /app/suggestion/
COPY related/ /app/related/
COPY multiagent/ /app/multiagent/
COPY entrypoint.sh /app/entrypoint.sh

# Create shared virtual environment
RUN python -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

# Install dependencies if requirements exist
RUN if [ -f /app/suggestion/requirements.txt ]; then pip install --no-cache-dir -r /app/suggestion/requirements.txt; fi && \
    if [ -f /app/related/requirements.txt ]; then pip install --no-cache-dir -r /app/related/requirements.txt; fi && \
    if [ -f /app/multiagent/requirements.txt ]; then pip install --no-cache-dir -r /app/multiagent/requirements.txt; fi

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000 8001 8002

ENTRYPOINT ["/app/entrypoint.sh"]
