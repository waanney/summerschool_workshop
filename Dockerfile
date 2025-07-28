# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code
COPY . .

# Install Python dependencies
RUN uv sync --frozen

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Default command to run Chainlit
CMD ["uv", "run", "chainlit", "run", "workflow/SAMPLE.py", "--host", "0.0.0.0", "--port", "8000"]