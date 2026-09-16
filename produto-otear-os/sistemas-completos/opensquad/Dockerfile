# Stage 1: Build Next.js app + compile worker
FROM node:22-alpine AS builder
WORKDIR /build

# Build args for Next.js (NEXT_PUBLIC_* must be available at build time)
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_WS_PORT=3001
ARG NEXT_PUBLIC_OFFICE3D_PORT=4200

COPY interface-app/package.json interface-app/package-lock.json ./
RUN npm ci

COPY interface-app/ ./
RUN npm run build

# Compile worker + ws-gateway to standalone JS bundles (all deps inlined)
RUN npx esbuild src/worker/index.ts --bundle --platform=node --target=node22 --outfile=dist/worker.js && \
    npx esbuild src/lib/ws-gateway.ts --bundle --platform=node --target=node22 --outfile=dist/ws-gateway.js

# Stage 2: Production
FROM node:22-alpine AS runner

# Install system deps (chromium for slide rendering)
RUN apk add --no-cache python3 bash curl git chromium

# Install Claude CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Create user with home directory
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --home /home/appuser appuser
RUN mkdir -p /home/appuser/.claude && \
    chown -R appuser:appuser /home/appuser

WORKDIR /opensquad

# Copy opensquad project files
COPY squads/ ./squads/
COPY _opensquad/ ./_opensquad/
COPY skills/ ./skills/
COPY CLAUDE.md ./CLAUDE.md
COPY .claude/ ./.claude/
COPY agent-dashboard.config.json ./agent-dashboard.config.json

# Copy 3D office dashboard server (no build step needed — vanilla JS + Three.js)
COPY agent-dashboard-main/server.js ./office3d-server.js
COPY agent-dashboard-main/scanner.js ./office3d-scanner.js
COPY agent-dashboard-main/public/ ./office3d-public/

# Copy Next.js standalone build (includes public/office/ with pixel-agents)
COPY --from=builder /build/.next/standalone ./app/
COPY --from=builder /build/.next/static ./app/.next/static
COPY --from=builder /build/public ./app/public

# Copy compiled worker + ws-gateway (self-contained JS bundles, zero runtime deps)
COPY --from=builder /build/dist/worker.js ./app/worker.js
COPY --from=builder /build/dist/ws-gateway.js ./app/ws-gateway.js

# Copy entrypoints and fix line endings
COPY entrypoint.sh ./app/entrypoint.sh
COPY entrypoint-worker.sh ./app/entrypoint-worker.sh
RUN sed -i 's/\r$//' ./app/entrypoint.sh && chmod +x ./app/entrypoint.sh && \
    sed -i 's/\r$//' ./app/entrypoint-worker.sh && chmod +x ./app/entrypoint-worker.sh

# Create directories
RUN mkdir -p /opensquad/squads/noticias-carrossel-ia/output && \
    mkdir -p /opensquad/data && \
    chown -R appuser:appuser /opensquad

# Environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
ENV OPENSQUAD_ROOT=/opensquad
ENV DATA_ROOT=/opensquad/data
ENV HOME=/home/appuser
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

USER appuser
EXPOSE 3000

WORKDIR /opensquad/app
ENTRYPOINT ["bash", "entrypoint.sh"]
