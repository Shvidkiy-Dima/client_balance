from .base import BaseConfig

class DevConfig(BaseConfig):
    DB_NAME = 'test_flask'
    DB_USER = 'admin'
    DB_PASSWORD = 'admin'
    DB_HOST = 'localhost'
    DEBUG = True