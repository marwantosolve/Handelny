#!/bin/bash
set -e

echo "🚀 Setting up Handelny development environment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed. Run: npm i -g pnpm"
    exit 1
fi

# Setup environment variables
if [ ! -f .env ]; then
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
fi

# Install dependencies
echo "📦 Installing Monorepo dependencies..."
pnpm install

# Start infrastructure
echo "🐳 Starting Docker Compose (Postgres, Redis, Qdrant, MinIO)..."
docker compose -f docker/docker-compose.yml up -d

echo "✅ Setup complete! You can now run:"
echo "   pnpm dev"
echo ""
echo "URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000/docs"
echo "- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)"
echo "- Qdrant Dashboard: http://localhost:6333/dashboard"
