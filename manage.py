#!/Users/sangwoo/Desktop/test/MidasServer/.env/bin/python
# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from main import app, db
# from everyzone.manage.geo import GeoCommand
# from everyzone.manage.chat import ChatCommand
# from everyzone.manage.users import UserCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
# manager.add_command('geo', GeoCommand)
# manager.add_command('chat', ChatCommand)
# manager.add_command('user', UserCommand)

@manager.command
def run():
    """Run server
    """
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    manager.run()
