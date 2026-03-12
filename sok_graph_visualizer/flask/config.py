"""
Configuration for Flask application
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Core paths
    BASE_DIR = Path(__file__).parent
    CORE_DIR = BASE_DIR.parent.parent / 'core'
    TEMPLATE_DIR = CORE_DIR / 'src' / 'web' / 'templates'
    STATIC_DIR = CORE_DIR / 'src' / 'web' / 'static'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
