# coding: utf-8

from flask_script import Manager, Shell, Command
from flask_migrate import MigrateCommand

from app import application
from app.celery import celery


def _make_context():
    return dict(app=application, celery=celery)

manager = Manager(application)
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context))

if __name__ == '__main__':
    manager.run()
