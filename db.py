import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app, Flask


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _query_property = None

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    @property
    def query(cls):

        if not hasattr(current_app, 'session'):
            raise RuntimeError('You have to call init_db before')

        if cls._query_property is not None:
            return cls._query_property

        cls._query_property = current_app.session.query_property()
        return cls._query_property


def init_db(config):
    db_name = config.get('DB_NAME')
    db_user = config.get('DB_USER')
    db_password = config.get('DB_PASSWORD')
    db_host = config.get('DB_HOST')

    if not all([db_host, db_user, db_password, db_name]):
        raise RuntimeError('You have to set DB_NAME DB_USER DB_PASSWORD DB_HOST in config')

    engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}')

    import apps.account.models
    BaseModel.metadata.create_all(bind=engine)
    return engine


def init_app_db(app: Flask):

    engine = init_db(app.config)

    app.session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False,
                                              bind=engine))

    @app.teardown_appcontext
    def remove_session(*args, **kwargs):
        app.session.remove()


