# Environment Configuration

## Environment Variables

### Required Variables

```env
# Core API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=your_milvus_token_here

# Memory Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# Email Configuration
SENDER_EMAIL=your_bot_email@gmail.com
SENDER_PASSWORD=your_app_password

# API Configuration
API_HOST=127.0.0.1
API_PORT=7000
ENVIRONMENT=development
```

### Optional Variables

```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_REQUESTS_PER_DAY=1000

# External Services
OPENWEATHER_API_KEY=your_weather_api_key
STORE_API_KEY=your_store_api_key

# Database
DATABASE_URL=sqlite:///app.db
BACKUP_INTERVAL=3600

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret
```

## Environment Setup for Different Stages

### Development Environment (.env.development)

```env
# Development Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Local Services
GEMINI_API_KEY=your_dev_gemini_key
OPENAI_API_KEY=your_dev_openai_key
MILVUS_URI=http://localhost:19530
REDIS_HOST=localhost
REDIS_PORT=6379

# Development Email (use mailtrap or similar)
SENDER_EMAIL=test@example.com
SENDER_PASSWORD=test_password

# Relaxed Rate Limits
RATE_LIMIT_PER_MINUTE=100
MAX_REQUESTS_PER_DAY=10000
```

### Production Environment (.env.production)

```env
# Production Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Production Services
GEMINI_API_KEY=your_prod_gemini_key
OPENAI_API_KEY=your_prod_openai_key
MILVUS_URI=https://your-milvus-cloud.com
MILVUS_TOKEN=your_prod_milvus_token

# Redis Cloud
REDIS_HOST=redis-cloud-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Production Email
SENDER_EMAIL=noreply@yourcompany.com
SENDER_PASSWORD=your_secure_app_password

# Production Rate Limits
RATE_LIMIT_PER_MINUTE=30
MAX_REQUESTS_PER_DAY=5000

# Security
SECRET_KEY=your_very_secure_secret_key
JWT_SECRET=your_jwt_secret_key
```

### Testing Environment (.env.testing)

```env
# Testing Configuration
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=ERROR

# Test Services
GEMINI_API_KEY=test_gemini_key
OPENAI_API_KEY=test_openai_key
MILVUS_URI=http://localhost:19530
REDIS_HOST=localhost
REDIS_PORT=6379

# Test Database
DATABASE_URL=sqlite:///:memory:

# Disabled External Services
SENDER_EMAIL=test@example.com
SENDER_PASSWORD=test

# No Rate Limits in Testing
RATE_LIMIT_PER_MINUTE=1000
MAX_REQUESTS_PER_DAY=100000
```

## Configuration Management

### 1. Using python-dotenv

```python
# config/env_loader.py
import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables based on ENVIRONMENT setting."""
    
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Load base .env file
    load_dotenv('.env')
    
    # Load environment-specific file
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    
    return env

# Usage
current_env = load_environment()
print(f"Running in {current_env} environment")
```

### 2. Environment Validation

```python
# config/validation.py
import os
from typing import List, Optional

class EnvironmentError(Exception):
    """Custom exception for environment configuration errors."""
    pass

def validate_required_vars(required_vars: List[str]) -> None:
    """Validate that all required environment variables are set."""
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

def validate_environment() -> None:
    """Validate all environment variables."""
    
    # Core required variables
    required_vars = [
        'GEMINI_API_KEY',
        'OPENAI_API_KEY',
        'MILVUS_URI'
    ]
    
    validate_required_vars(required_vars)
    
    # Validate API keys format
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and not gemini_key.startswith('AI'):
        print("Warning: GEMINI_API_KEY might be invalid")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and not openai_key.startswith('sk-'):
        print("Warning: OPENAI_API_KEY might be invalid")
    
    # Validate numeric values
    try:
        port = int(os.getenv('API_PORT', '7000'))
        if port < 1 or port > 65535:
            raise ValueError("API_PORT must be between 1 and 65535")
    except ValueError as e:
        raise EnvironmentError(f"Invalid API_PORT: {e}")
    
    print("✓ Environment validation passed")

# Usage
if __name__ == "__main__":
    try:
        validate_environment()
    except EnvironmentError as e:
        print(f"❌ Environment validation failed: {e}")
        exit(1)
```

### 3. Configuration Class

```python
# config/settings.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    milvus_uri: str
    milvus_token: Optional[str]
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: Optional[str]

@dataclass
class APIConfig:
    gemini_api_key: str
    openai_api_key: str
    rate_limit_per_minute: int
    max_requests_per_day: int

@dataclass
class EmailConfig:
    sender_email: str
    sender_password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

@dataclass
class AppConfig:
    environment: str
    debug: bool
    log_level: str
    host: str
    port: int
    secret_key: str

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        self.database = DatabaseConfig(
            milvus_uri=os.getenv('MILVUS_URI', 'http://localhost:19530'),
            milvus_token=os.getenv('MILVUS_TOKEN'),
            redis_host=os.getenv('REDIS_HOST', 'localhost'),
            redis_port=int(os.getenv('REDIS_PORT', '6379')),
            redis_db=int(os.getenv('REDIS_DB', '0')),
            redis_password=os.getenv('REDIS_PASSWORD')
        )
        
        self.api = APIConfig(
            gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
            max_requests_per_day=int(os.getenv('MAX_REQUESTS_PER_DAY', '1000'))
        )
        
        self.email = EmailConfig(
            sender_email=os.getenv('SENDER_EMAIL', ''),
            sender_password=os.getenv('SENDER_PASSWORD', ''),
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587'))
        )
        
        self.app = AppConfig(
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            host=os.getenv('API_HOST', '127.0.0.1'),
            port=int(os.getenv('API_PORT', '7000')),
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key')
        )
    
    def is_development(self) -> bool:
        return self.app.environment == 'development'
    
    def is_production(self) -> bool:
        return self.app.environment == 'production'
    
    def is_testing(self) -> bool:
        return self.app.environment == 'testing'

# Global settings instance
settings = Settings()
```
## Environment Management Scripts

### 1. Environment Setup Script

```bash
#!/bin/bash
# scripts/setup_env.sh

set -e

ENVIRONMENT=${1:-development}

echo "Setting up environment: $ENVIRONMENT"

# Create environment file
if [ ! -f ".env.${ENVIRONMENT}" ]; then
    echo "Creating .env.${ENVIRONMENT} from template"
    cp .env.template .env.${ENVIRONMENT}
    
    echo "Please edit .env.${ENVIRONMENT} with your actual values"
    exit 1
fi

# Copy environment file
cp .env.${ENVIRONMENT} .env

# Validate environment
python -c "from config.validation import validate_environment; validate_environment()"

echo "✓ Environment setup complete for: $ENVIRONMENT"
```

### 2. Environment Switching Script

```bash
#!/bin/bash
# scripts/switch_env.sh

ENVIRONMENT=${1:-development}

if [ ! -f ".env.${ENVIRONMENT}" ]; then
    echo "Environment file .env.${ENVIRONMENT} not found"
    exit 1
fi

# Backup current environment
if [ -f ".env" ]; then
    cp .env .env.backup
fi

# Switch environment
cp .env.${ENVIRONMENT} .env

echo "Switched to environment: $ENVIRONMENT"
echo "Previous environment backed up to .env.backup"
```

### 3. Environment Validation Script

```python
#!/usr/bin/env python3
# scripts/validate_env.py

import os
import sys
from config.validation import validate_environment
from config.env_loader import load_environment

def main():
    """Validate current environment configuration."""
    
    try:
        # Load environment
        env = load_environment()
        print(f"Environment: {env}")
        
        # Validate configuration
        validate_environment()
        
        print("✓ All environment validations passed")
        
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Security

```python
# Never commit secrets to version control
# Use .env files for local development
# Use environment variables in production
# Rotate API keys regularly
# Use different keys for different environments

# Example: Secure key loading
import os
from cryptography.fernet import Fernet

def load_encrypted_key(key_name: str) -> str:
    """Load encrypted API key from environment."""
    
    encrypted_key = os.getenv(f"{key_name}_ENCRYPTED")
    encryption_key = os.getenv("ENCRYPTION_KEY")
    
    if not encrypted_key or not encryption_key:
        raise ValueError(f"Missing encrypted key or encryption key for {key_name}")
    
    cipher_suite = Fernet(encryption_key.encode())
    decrypted_key = cipher_suite.decrypt(encrypted_key.encode())
    
    return decrypted_key.decode()
```

### 2. Configuration Templates

```env
# .env.template
# Copy this file to .env and fill in your values

# Core API Keys (Required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=your_milvus_token_here

# Memory Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Settings (Optional)
SENDER_EMAIL=your_email@example.com
SENDER_PASSWORD=your_app_password

# Application Settings
API_HOST=127.0.0.1
API_PORT=7000
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 3. Environment Documentation

```markdown
# Environment Variables Documentation

## Core Variables

### GEMINI_API_KEY
- **Required**: Yes
- **Description**: Google Gemini API key for LLM functionality
- **Format**: String starting with "AI"
- **Example**: `AIzaSyC...`

### OPENAI_API_KEY
- **Required**: Yes
- **Description**: OpenAI API key for embeddings
- **Format**: String starting with "sk-"
- **Example**: `sk-...`

### MILVUS_URI
- **Required**: Yes
- **Description**: Milvus database connection URI
- **Format**: URL
- **Example**: `http://localhost:19530`

## Optional Variables

### REDIS_HOST
- **Required**: No
- **Default**: localhost
- **Description**: Redis server hostname
- **Example**: `redis.example.com`

### RATE_LIMIT_PER_MINUTE
- **Required**: No
- **Default**: 60
- **Description**: API rate limit per minute
- **Example**: `100`
```

Cấu hình environment đúng cách là rất quan trọng để đảm bảo hệ thống hoạt động ổn định và bảo mật trong các môi trường khác nhau!
