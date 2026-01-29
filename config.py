"""
Production configuration for StatBot Pro
Centralized configuration management with environment variable support
"""

import os
from pathlib import Path
from typing import List, Dict, Any

class Config:
    """Production configuration class"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8001))
    WORKERS: int = int(os.getenv("WORKERS", 1))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Security Configuration
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8001,http://localhost:8080").split(",")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", 100000))
    MAX_COLUMNS: int = int(os.getenv("MAX_COLUMNS", 1000))
    ALLOWED_EXTENSIONS: List[str] = ['.csv']
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", 3600))  # 1 hour
    
    # Execution Limits
    EXECUTION_TIMEOUT: int = int(os.getenv("EXECUTION_TIMEOUT", 30))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    MAX_MEMORY_MB: int = int(os.getenv("MAX_MEMORY_MB", 512))
    MAX_CPU_TIME: int = int(os.getenv("MAX_CPU_TIME", 30))
    
    # Directory Configuration
    BASE_DIR: Path = Path(__file__).parent
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Cleanup Configuration
    CLEANUP_INTERVAL: int = int(os.getenv("CLEANUP_INTERVAL", 3600))  # 1 hour
    FILE_RETENTION_HOURS: int = int(os.getenv("FILE_RETENTION_HOURS", 24))
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("SESSION_TIMEOUT_HOURS", 24))
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", 9090))
    
    # Database Configuration (for future use)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///statbot.db")
    
    @classmethod
    def setup_directories(cls) -> None:
        """Create necessary directories"""
        directories = [cls.WORKSPACE_DIR, cls.STATIC_DIR, cls.TEMPLATES_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(exist_ok=True, mode=0o755)
    
    @classmethod
    def get_uvicorn_config(cls) -> Dict[str, Any]:
        """Get uvicorn server configuration"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "workers": 1,  # Force single worker for in-memory session storage
            "log_level": cls.LOG_LEVEL,
            "access_log": True,
            "reload": cls.ENVIRONMENT == "development",
            "loop": "asyncio"
        }
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.ENVIRONMENT == "production"

# Create global config instance
config = Config()

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    LOG_LEVEL = "debug"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for development
    RATE_LIMIT_REQUESTS = 1000  # More lenient for development

class ProductionConfig(Config):
    """Production environment configuration"""
    LOG_LEVEL = "info"
    WORKERS = int(os.getenv("WORKERS", 4))  # More workers for production
    
class TestingConfig(Config):
    """Testing environment configuration"""
    LOG_LEVEL = "warning"
    MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB for testing
    EXECUTION_TIMEOUT = 10  # Shorter timeout for tests
    RATE_LIMIT_REQUESTS = 10000  # Very lenient for testing

# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return ProductionConfig()