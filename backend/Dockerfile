FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for Claude CLI and ffmpeg for frame extraction
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Create data directory for transcript cache (will be mounted as volume)
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# Create .claude directory for credentials (will be mounted as volume)
RUN mkdir -p /home/appuser/.claude && chown -R appuser:appuser /home/appuser

# Copy application code with ownership
COPY --chown=appuser:appuser . .

USER appuser

# Set HOME for claude CLI to find credentials
ENV HOME=/home/appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
