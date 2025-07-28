.PHONY: help setup build up down logs clean restart status

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Copy .env.template to .env for configuration"
	@echo "  build     - Build the Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, volumes, and images"
	@echo "  restart   - Restart all services"
	@echo "  status    - Show status of all services"
	@echo "  up-deps   - Start only dependencies (Milvus, Redis)"
	@echo "  app-logs  - Show logs from main application only"

# Setup environment file
setup:
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "Created .env file from template. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi

# Build Docker images
build:
	docker-compose build

# Start all services
up: setup
	docker-compose up -d
	@echo "Services started. Access the application at:"
	@echo "  - Milvus: http://localhost:19530"
	@echo "  - MinIO Console: http://localhost:9001"
	@echo "  - Redis: localhost:6379"

# Start only dependencies
up-deps: setup
	docker-compose up -d etcd minio milvus redis
	@echo "Dependencies started. You can now run the app locally."

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Show logs from main application only
app-logs:
	docker-compose logs -f app

# Clean up everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Restart all services
restart:
	docker-compose restart

# Show status of services
status:
	docker-compose ps

# Development commands
dev-build:
	docker-compose build --no-cache

dev-up: setup
	docker-compose up

# Health check
health:
	@echo "Checking service health..."
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

up-chatbot: setup
	@echo "🎨 Starting Makeup Chatbot Setup..."
	@echo "📦 Installing UV package manager..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh || pip install uv
	@echo "📚 Installing Python dependencies..."
	@uv sync
	@echo "🐳 Building and starting services..."
	@docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 15
	@echo "🎉 Makeup Chatbot is ready!"
	@echo "🌐 Access at: http://localhost:8000"
	@echo "📋 To view logs: make app-logs"
	@echo "🛑 To stop: make down"
