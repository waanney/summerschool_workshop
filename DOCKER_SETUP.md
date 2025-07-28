# Docker Setup Guide

This guide explains how to run the Summerschool Workshop project using Docker for easy deployment across different machines.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd summerschool_workshop
   ```

2. **Set up environment variables**
   ```bash
   make setup
   ```
   This will create a `.env` file from the template. Edit it with your API keys:
   ```bash
   # Edit the .env file
   nano .env  # or use your preferred editor
   ```

3. **Start all services**
   ```bash
   make up
   ```

4. **Access the application**
   - **Chainlit Interface**: http://localhost:8000
   - **Milvus Admin**: http://localhost:19530
   - **MinIO Console**: http://localhost:9001 (admin/minioadmin)
   - **Redis**: localhost:6379

## Available Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make setup` | Create .env file from template |
| `make build` | Build Docker images |
| `make up` | Start all services |
| `make down` | Stop all services |
| `make logs` | Show logs from all services |
| `make app-logs` | Show logs from main application only |
| `make restart` | Restart all services |
| `make status` | Show status of all services |
| `make clean` | Remove all containers, volumes, and images |
| `make up-deps` | Start only dependencies (for local development) |
| `make health` | Check service health status |

## Services Overview

### Main Application
- **Port**: 8000
- **Description**: Chainlit-based web interface for the chatbot
- **Dependencies**: Milvus, Redis

### Milvus (Vector Database)
- **Port**: 19530
- **Description**: Vector database for semantic search
- **Dependencies**: etcd, MinIO
- **Data**: Persisted in `milvus_data` volume

### Redis (Cache)
- **Port**: 6379
- **Description**: In-memory cache for session management
- **Data**: Persisted in `redis_data` volume

### Supporting Services
- **etcd**: Configuration store for Milvus
- **MinIO**: Object storage for Milvus

## Environment Variables

Required environment variables in `.env` file:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Milvus Configuration (optional for Docker setup)
MILVUS_URI=http://milvus:19530
MILVUS_TOKEN=

# Application Settings (optional)
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Development Workflow

### For Full Docker Development
```bash
# Start all services
make up

# View logs
make logs

# Stop services
make down
```

### For Local Development with Docker Dependencies
```bash
# Start only external dependencies
make up-deps

# Run the app locally
uv run chainlit run workflow/SAMPLE.py --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   - Check if ports 8000, 19530, 6379, 9000, 9001 are available
   - Stop conflicting services or modify ports in `docker-compose.yml`

2. **Memory issues**
   - Milvus requires at least 4GB RAM
   - Increase Docker memory allocation if needed

3. **Permission issues**
   - Ensure Docker daemon is running
   - Check user permissions for Docker

### Checking Service Health
```bash
# Check all services status
make status

# Check detailed health
make health

# View specific service logs
docker-compose logs -f milvus
docker-compose logs -f redis
docker-compose logs -f app
```

### Resetting Everything
```bash
# Stop and remove everything
make clean

# Start fresh
make up
```

## Data Persistence

The following data is persisted across container restarts:
- **Milvus data**: Vector embeddings and collections
- **Redis data**: Cache and session data
- **MinIO data**: Object storage
- **Application logs**: Stored in `./logs` directory

## Production Considerations

1. **Security**
   - Change default MinIO credentials
   - Use proper authentication for Milvus
   - Set up proper firewall rules

2. **Monitoring**
   - Monitor container health
   - Set up log aggregation
   - Monitor resource usage

3. **Backup**
   - Regular backup of Docker volumes
   - Backup environment configuration

## Support

If you encounter issues:
1. Check the logs: `make logs`
2. Verify service status: `make status`
3. Try restarting: `make restart`
4. Clean and rebuild: `make clean && make up`