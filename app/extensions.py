# coding: utf-8

from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app import config

db = SQLAlchemy(session_options={
    'expire_on_commit': False
})
migrate = Migrate()


def make_celery(app):
    celery = Celery(app.name,
                    broker=config.CELERY_BROKER_URL)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
