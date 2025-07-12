# Deployment Guide

## 🚀 Deployment Options

### 1. Local Development
- Single machine deployment
- Development và testing
- Quick prototyping

### 2. Docker Deployment
- Containerized deployment
- Consistent environments
- Easy scaling

### 3. Cloud Deployment
- Production-ready
- Auto-scaling
- High availability

### 4. Kubernetes Deployment
- Container orchestration
- Advanced scaling
- Enterprise-grade

## 🐳 Docker Deployment

### 1. Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      - ENVIRONMENT=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MILVUS_URI=http://milvus:19530
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - milvus
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:v2.5.0
    ports:
      - "19530:19530"
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    depends_on:
      - etcd
      - minio
    volumes:
      - milvus_data:/var/lib/milvus
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped

  etcd:
    image: quay.io/coreos/etcd:v3.5.0
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    volumes:
      - etcd_data:/etcd
    restart: unless-stopped

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    ports:
      - "9000:9000"
    command: minio server /minio_data --console-address ":9001"
    volumes:
      - minio_data:/minio_data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  milvus_data:
  redis_data:
  etcd_data:
  minio_data:
```

### 2. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "app.py"]
```

### 3. nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 10M;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /health {
            proxy_pass http://app/health;
        }
    }
}
```

### 4. Deployment Commands

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3

# Update deployment
docker-compose pull
docker-compose up -d

# Backup data
docker-compose exec milvus mkdir -p /backup
docker-compose exec redis redis-cli BGSAVE

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### 1. AWS Deployment

#### ECS Fargate
```yaml
# ecs-task-definition.json
{
    "family": "summerschool-workshop",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "app",
            "image": "your-repo/summerschool-workshop:latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "ENVIRONMENT",
                    "value": "production"
                }
            ],
            "secrets": [
                {
                    "name": "GEMINI_API_KEY",
                    "valueFrom": "arn:aws:secretsmanager:region:account:secret:gemini-api-key"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/summerschool-workshop",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
```

#### CloudFormation Template
```yaml
# cloudformation.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Summerschool Workshop Deployment'

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
  
Resources:
  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: summerschool-workshop
      
  # Application Load Balancer
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: summerschool-workshop-alb
      Subnets: !Ref SubnetIds
      SecurityGroups:
        - !Ref ALBSecurityGroup
        
  # RDS for persistent storage
  RDSInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: summerschool-workshop-db
      DBInstanceClass: db.t3.micro
      Engine: postgres
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      
  # ElastiCache for Redis
  ElastiCacheCluster:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t3.micro
      Engine: redis
      NumCacheNodes: 1
```

### 2. Google Cloud Platform

#### Cloud Run Deployment
```yaml
# cloud-run.yml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: summerschool-workshop
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "2Gi"
        run.googleapis.com/cpu: "1000m"
    spec:
      containers:
      - image: gcr.io/PROJECT-ID/summerschool-workshop:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: key
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
```

#### Deployment Script
```bash
#!/bin/bash
# deploy-gcp.sh

PROJECT_ID="your-project-id"
REGION="us-central1"

# Build and push image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/summerschool-workshop:latest

# Deploy to Cloud Run
gcloud run deploy summerschool-workshop \
    --image gcr.io/${PROJECT_ID}/summerschool-workshop:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10

# Set up secrets
gcloud secrets create gemini-api-key --data-file=api-key.txt
gcloud secrets create openai-api-key --data-file=openai-key.txt

# Update service with secrets
gcloud run services update summerschool-workshop \
    --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
    --update-secrets=OPENAI_API_KEY=openai-api-key:latest \
    --region ${REGION}
```

### 3. Azure Deployment

#### Container Instances
```yaml
# azure-container-instance.yml
apiVersion: 2019-12-01
location: eastus
name: summerschool-workshop
properties:
  containers:
  - name: app
    properties:
      image: yourregistry.azurecr.io/summerschool-workshop:latest
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: ENVIRONMENT
        value: production
      - name: GEMINI_API_KEY
        secureValue: your-gemini-api-key
      resources:
        requests:
          cpu: 1
          memoryInGB: 2
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

## ⚙️ Kubernetes Deployment

### 1. Kubernetes Manifests

```yaml
# k8s/namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: summerschool-workshop
---
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: summerschool-workshop
  namespace: summerschool-workshop
spec:
  replicas: 3
  selector:
    matchLabels:
      app: summerschool-workshop
  template:
    metadata:
      labels:
        app: summerschool-workshop
    spec:
      containers:
      - name: app
        image: your-registry/summerschool-workshop:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: gemini-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        - name: MILVUS_URI
          value: "http://milvus:19530"
        - name: REDIS_HOST
          value: "redis"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# k8s/service.yml
apiVersion: v1
kind: Service
metadata:
  name: summerschool-workshop
  namespace: summerschool-workshop
spec:
  selector:
    app: summerschool-workshop
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
# k8s/ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: summerschool-workshop
  namespace: summerschool-workshop
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: summerschool-workshop-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: summerschool-workshop
            port:
              number: 80
```

### 2. Secrets Management

```yaml
# k8s/secrets.yml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: summerschool-workshop
type: Opaque
data:
  gemini-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
---
# k8s/configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: summerschool-workshop
data:
  ENVIRONMENT: production
  LOG_LEVEL: INFO
  RATE_LIMIT_PER_MINUTE: "30"
```

### 3. Helm Chart

```yaml
# helm/Chart.yml
apiVersion: v2
name: summerschool-workshop
description: A Helm chart for Summerschool Workshop
type: application
version: 0.1.0
appVersion: "1.0.0"
---
# helm/values.yml
replicaCount: 3

image:
  repository: your-registry/summerschool-workshop
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: summerschool-workshop-tls
      hosts:
        - yourdomain.com

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

milvus:
  enabled: true
  image:
    repository: milvusdb/milvus
    tag: v2.5.0

redis:
  enabled: true
  image:
    repository: redis
    tag: 7-alpine
```

## 🔧 Configuration Management

### 1. Environment-specific Configs

```yaml
# config/production.yml
database:
  milvus:
    uri: "https://your-milvus-cloud.com"
    timeout: 30
  redis:
    host: "your-redis-cluster.com"
    port: 6379
    ssl: true

api:
  rate_limit: 30
  timeout: 60
  max_requests_per_day: 5000

logging:
  level: WARNING
  format: json
  
security:
  cors_origins: ["https://yourdomain.com"]
  https_only: true
  secure_cookies: true
```

### 2. Feature Flags

```python
# config/feature_flags.py
import os

class FeatureFlags:
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true'
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    
    @classmethod
    def get_all_flags(cls):
        return {
            'caching': cls.ENABLE_CACHING,
            'analytics': cls.ENABLE_ANALYTICS,
            'rate_limiting': cls.ENABLE_RATE_LIMITING,
            'max_upload_size': cls.MAX_UPLOAD_SIZE
        }
```

## 📊 Monitoring và Observability

### 1. Health Checks

```python
# app/health.py
from fastapi import FastAPI
from starlette.responses import JSONResponse
import asyncio

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ready")
async def readiness_check():
    """Readiness check with dependencies."""
    checks = {
        "milvus": await check_milvus_connection(),
        "redis": await check_redis_connection(),
        "api_keys": check_api_keys()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        content={"status": "ready" if all_healthy else "not_ready", "checks": checks},
        status_code=status_code
    )
```

### 2. Metrics Collection

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
TOOL_USAGE = Counter('tool_usage_total', 'Tool usage counter', ['tool_name'])

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Count request
            REQUEST_COUNT.labels(
                method=scope["method"],
                endpoint=scope["path"]
            ).inc()
            
            # Track duration
            response = await self.app(scope, receive, send)
            
            REQUEST_DURATION.observe(time.time() - start_time)
            
            return response
        
        return await self.app(scope, receive, send)
```

### 3. Logging Configuration

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured logging."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger
```

## 🔒 Security Hardening

### 1. Security Headers

```python
# security/headers.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
```

### 2. Rate Limiting

```python
# security/rate_limiting.py
from fastapi import HTTPException
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=60, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        
        # Clean old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check limit
        if len(self.clients[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.clients[client_id].append(now)
        return True
```

## 🚀 Deployment Automation

### 1. CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: pytest
    - name: Run security checks
      run: bandit -r src/
      
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: |
        docker build -t summerschool-workshop:${{ github.sha }} .
        docker tag summerschool-workshop:${{ github.sha }} summerschool-workshop:latest
    - name: Push to registry
      run: |
        docker push summerschool-workshop:${{ github.sha }}
        docker push summerschool-workshop:latest
        
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/summerschool-workshop \
          app=summerschool-workshop:${{ github.sha }}
        kubectl rollout status deployment/summerschool-workshop
```

### 2. Deployment Scripts

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

echo "Deploying to $ENVIRONMENT with version $VERSION"

# Build image
docker build -t summerschool-workshop:$VERSION .

# Push to registry
docker push summerschool-workshop:$VERSION

# Deploy based on environment
case $ENVIRONMENT in
  "production")
    kubectl set image deployment/summerschool-workshop app=summerschool-workshop:$VERSION
    kubectl rollout status deployment/summerschool-workshop
    ;;
  "staging")
    kubectl set image deployment/summerschool-workshop-staging app=summerschool-workshop:$VERSION
    kubectl rollout status deployment/summerschool-workshop-staging
    ;;
  "docker")
    docker-compose down
    docker-compose up -d
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT"
    exit 1
    ;;
esac

echo "Deployment completed successfully!"
```

## 📈 Performance Optimization

### 1. Database Optimization

```python
# optimization/database.py
from pymilvus import connections

class OptimizedMilvusClient:
    def __init__(self):
        # Connection pooling
        self.pool_size = 10
        self.connections = []
    
    async def get_connection(self):
        """Get connection from pool."""
        if not self.connections:
            await self.create_connections()
        return self.connections.pop()
    
    async def release_connection(self, conn):
        """Release connection back to pool."""
        self.connections.append(conn)
    
    async def batch_insert(self, data, batch_size=1000):
        """Insert data in batches."""
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            await self.insert_batch(batch)
```

### 2. Caching Strategy

```python
# optimization/caching.py
import redis
import json
import hashlib
from typing import Optional, Any

class CacheManager:
    def __init__(self, redis_client, default_ttl=3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key."""
        key_data = json.dumps(kwargs, sort_keys=True)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    async def get_or_set(self, key: str, func, ttl: Optional[int] = None):
        """Get from cache or set if not exists."""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        result = await func()
        await self.redis.setex(
            key, 
            ttl or self.default_ttl, 
            json.dumps(result)
        )
        return result
```

Deployment guide này cung cấp một framework hoàn chỉnh để deploy Summerschool Workshop từ development đến production scale! 🚀
