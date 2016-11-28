# coding: utf-8

from pymessenger import Bot

from flask import Flask, render_template

from . import config
from .extensions import db, migrate, make_celery
from . import models
from .imgur import ImgurApi


def create_app():
    app = Flask('picture-bot')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.celery = make_celery(app)
    app.bot = Bot(config.FACEBOOK_APP_TOKEN)
    app.imgur = ImgurApi(
        client_id=config.IMGUR_CLIENT_ID,
        client_secret=config.IMGUR_CLIENT_SECRET
    )

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def not_allowed(e):
        return render_template('403.html'), 403

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html'), 403

    @app.errorhandler(500)
    def error(e):
        return render_template('500.html'), 500

    return app


application = create_app()

# import views to add view
from app import views
