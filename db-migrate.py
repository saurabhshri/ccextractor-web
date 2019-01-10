from run import app
from database import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from mod_auth.models import AccountType, Users
from mod_dashboard.models import ProcessStauts, Platforms, UploadedFiles, ProcessQueue, CCExtractorVersions, CCExtractorParameters, DetailsForTemplate
from mod_kvm.models import KVM, VM, KVM_cmds, KVM_Status
from mod_landing.models import LandingPageStatistics

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
