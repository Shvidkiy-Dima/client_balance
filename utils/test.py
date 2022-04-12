from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from db import BaseModel


@contextmanager
def create_test_db():
    from settings.test import TestConfig as Config

    db_name = Config.DB_NAME
    db_user = Config.DB_USER
    db_password = Config.DB_PASSWORD
    db_host = Config.DB_HOST

    if not all([db_host, db_user, db_password, db_name]):
        raise RuntimeError('You have to set DB_NAME DB_USER DB_PASSWORD DB_HOST in config')

    engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/postgres', )
    conn = engine.connect()
    conn.execute("commit")
    conn.execute(f'DROP DATABASE IF EXISTS {db_name}')
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {db_name}")

    engine2 = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}' )

    import apps.account.models
    BaseModel.metadata.create_all(bind=engine2)
    try:
        yield
    finally:
        try:
            conn.execute("commit")
            conn.execute(f"DROP DATABASE {db_name}")
            conn.close()
            print('closed')
        except Exception:
            pass


@contextmanager
def get_test_session():
    from settings.test import TestConfig as Config

    db_name = Config.DB_NAME
    db_user = Config.DB_USER
    db_password = Config.DB_PASSWORD
    db_host = Config.DB_HOST

    if not all([db_host, db_user, db_password, db_name]):
        raise RuntimeError('You have to set DB_NAME DB_USER DB_PASSWORD DB_HOST in config')

    engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}' )

    try:
        yield scoped_session(sessionmaker(autocommit=False,
                                                  autoflush=False,
                                                  bind=engine))
    finally:
        engine.connect().close()
