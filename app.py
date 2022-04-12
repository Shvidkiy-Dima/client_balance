from flask import Flask
from db import init_app_db
from flasgger import Swagger


def create_app():
    from settings import Config

    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    init_app_db(app)

    from apps import account
    app.register_blueprint(account.bp, url_prefix='/api/account')

    Swagger(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(threaded=True)
