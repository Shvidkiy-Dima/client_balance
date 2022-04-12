from .base import BaseConfig


class TestConfig(BaseConfig):
    DB_NAME = 'test_database'
    DB_USER = 'admin'
    DB_PASSWORD = 'admin'
    DB_HOST = 'db'
    HOST = 'localhost'
    PORT = 5001
