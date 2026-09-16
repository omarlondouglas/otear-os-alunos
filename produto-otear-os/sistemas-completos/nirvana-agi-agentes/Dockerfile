FROM python:3.11-slim-bookworm

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_NO_CACHE_DIR=1
ENV NODE_OPTIONS=--max-old-space-size=4096
ENV REFERENCES_PATH=/app/storage/references

# Install system dependencies
# Added libsndfile1 for audio processing (faster-whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    libpq-dev \
    libmagic1 \
    libopenblas-dev \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    curl \
    git \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavdevice-dev \
    libavfilter-dev \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS + Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && npm install -g @openai/codex \
    && rm -rf /var/lib/apt/lists/*

# Preparar diretórios para credenciais e storage
RUN mkdir -p /root/.claude /root/.codex /app/storage /app/var/logs /app/var/tmp /app/var/downloads /app/var/cache

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install heavy ML dependencies first to optimize caching
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements
COPY requirements.txt .

# Install remaining Python dependencies
RUN pip install -r requirements.txt


# Copy application code
COPY . .

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Entrypoint robusto — valida CLI e credenciais antes de iniciar
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000 8001

# Entrypoint valida credenciais, CMD inicia serviços
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
