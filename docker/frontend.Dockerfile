# Build context is the repo root (see docker/docker-compose.yml).
FROM node:20-alpine

RUN corepack enable && corepack prepare pnpm@9.0.0 --activate

WORKDIR /repo

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml turbo.json ./
COPY packages/ packages/
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --frozen-lockfile

COPY apps/web/ apps/web/

WORKDIR /repo/apps/web

EXPOSE 3000

CMD ["pnpm", "dev"]
