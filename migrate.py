import os
import unittest
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app

#pass configurations and inititalize the app
app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)

#instantiate a class that will manage init, migrate,downgrade and upgrade
manager = Manager(app)

#define the migration
manager.add_command('db', MigrateCommand)

#use migrations for testing function
@manager.command
def run_tests():
    #testing without test coverage
    tests =unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
