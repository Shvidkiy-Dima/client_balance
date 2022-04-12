import os


class BaseConfig:
    DB_NAME = os.environ.get('POSTGRES_DB')
    DB_USER = os.environ.get('POSTGRES_USER')
    DB_PASSWORD = os.environ.get('POSTGRES_PASS')
    DB_HOST = os.environ.get('POSTGRES_HOST')

    @classmethod
    def get(cls, value):
        return getattr(cls, value, None)
