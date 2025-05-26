# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("helloSecurity.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from helloSecurity.routes.restaurant import bp as restaurants_bp
    app.register_blueprint(restaurants_bp)

    return app