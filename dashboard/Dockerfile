# syntax=docker/dockerfile:1.7
# ─── Stage 1: install dependencies ────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci


# ─── Stage 2: build ───────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Ensure /app/public exists even if the project doesn't ship one — the runtime
# stage unconditionally copies it.
RUN mkdir -p public

# NEXT_PUBLIC_* values are baked into the JS bundle at build time, but in our
# setup the dashboard talks to the backend via the host's nginx — the actual
# value can be set at runtime via NEXT_PUBLIC_BACKEND_URL too because we use
# it in `next.config.mjs` rewrites (server-side) and `lib/server-api.ts`
# (server-side). So a build-time placeholder is fine.
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build


# ─── Stage 3: runtime (Next standalone) ───────────────────────────────────
FROM node:20-alpine AS runtime

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    TZ=Asia/Tashkent

# tzdata for Asia/Tashkent; create non-root user.
RUN apk add --no-cache tzdata curl \
 && addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 nextjs

WORKDIR /app

# Standalone output already includes a minimal node_modules and server.js.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:3000/login || exit 1

CMD ["node", "server.js"]
