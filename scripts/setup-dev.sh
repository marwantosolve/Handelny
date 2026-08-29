#!/bin/bash
set -e

echo "🚀 Setting up Handelny development environment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

# Setup environment variables
if [ ! -f .env ]; then
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "⚠️  Edit .env now and set GOOGLE_AI_STUDIO_API_KEY and JWT_SECRET before continuing."
fi

# Start everything (Postgres, Redis, Qdrant, MinIO, backend, frontend)
echo "🐳 Starting Docker Compose (this can take a few minutes on first run)..."
docker compose -f docker/docker-compose.yml up -d --build

echo "⏳ Waiting for the backend to become healthy..."
sleep 5

echo "🗄️  Running database migrations..."
docker compose -f docker/docker-compose.yml exec -T backend uv run alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API docs: http://localhost:8000/docs"
echo "- Backend health check: http://localhost:8000/api/v1/health"
echo "- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)"
echo "- Qdrant Dashboard: http://localhost:6333/dashboard"
