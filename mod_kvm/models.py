"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import enum
import libvirt
import pytz

from datetime import datetime
from tzlocal import get_localzone

from database import db
from logger import Logger


from mod_dashboard.models import Platforms

from config_parser import general_config


kvm_logger = Logger(log_level=general_config['LOG_LEVEL'],
                    dir=general_config['LOG_FILE_DIR'],
                    filename="kvm")
kvm_log = kvm_logger.get_logger("kvm")


class KVM_Status(enum.Enum):
    running = 'running'
    stopped = 'stopped'
    suspended = 'suspended'
    rebooting = 'rebooting'
    crashed = 'crashed'
    maintainance = 'maintainance'
    unknown = 'unknown'
    not_found = 'not_found'


class KVM_cmds(enum.Enum):
    start = 'start'
    shutdown = 'shutdown'
    stop = 'stop'
    snapshot = 'snapshot'
    suspend = 'suspend'
    resume = 'resume'
    reboot = 'reboot'
    maintain = 'maintain'  # suspend + db shows maintainance


class KVM(db.Model):
    __tablename__ = 'kvm'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    platform = db.Column(db.Enum(Platforms))
    status = db.Column(db.Enum(KVM_Status))
    start_timestamp = db.Column(db.DateTime())

    def __init__(self, name, platform, status, timestamp=None):
        self.name = name
        self.platform = platform
        self.status = status

        tz = get_localzone()

        if timestamp is None:
            timestamp = tz.localize(datetime.now(), is_dst=None)
            timestamp = timestamp.astimezone(pytz.UTC)

        if timestamp.tzinfo is None:
            timestamp = pytz.utc.localize(timestamp, is_dst=None)

        self.start_timestamp = timestamp

    def __repr__(self):
        return '<KVM : {id}>'.format(id=self.id)

    @db.reconstructor
    def may_the_timezone_be_with_it(self):
        """
        Localize the timestamp to utc
        """
        self.start_timestamp = pytz.utc.localize(self.start_timestamp, is_dst=None)


class VM():
    def __init__(self, name):
        self.name = name

        try:
            conn = libvirt.open("qemu:///system")
        except Exception as e:
            kvm_log.error("Exception occured while opening connection to libvirt : {e}".format(e=e))
            raise Exception("Could not open connection to libvirt! Exception : {e}".format(e=e))
        else:
            if conn is None:
                kvm_log.error("Could not open connection to libvirt!")
                raise Exception("Could not open connection to libvirt!")

        try:
            self.kvm = conn.lookupByName(name)
        except libvirt.libvirtError:
            kvm_log.error("Couldn't find KVM with name : {name}".format(name=name))
            raise Exception("Couldn't find KVM with name : {name}".format(name=name))

        state, reason = self.kvm.state()

        kvm_log.debug('Discovered state = {state}, reason = {reason}'.format(state=state, reason=reason))

        if state == libvirt.VIR_DOMAIN_RUNNING:
            self.status = KVM_Status.running
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            self.status = KVM_Status.suspended
        elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
            self.status = KVM_Status.rebooting
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            self.status = KVM_Status.stopped
        elif state == libvirt.VIR_DOMAIN_CRASHED:
            self.status = KVM_Status.crashed
        else:
            self.status = KVM_Status.unknown

        kvm_log.debug(' :: {name} :: Discovered state = {state}'.format(name=self.name, state=self.status))

    def __repr__(self):
        return '<VM : {name}'.format(name=self.name)

    def start(self):
        if self.status is KVM_Status.running:
            kvm_log.error(" :: {name} :: Already Running".format(name=self.name))
            return {'status': 'failed', 'reason': 'Already Running'}

        try:
            self.kvm.create()
            kvm_log.debug(" :: {name} :: Started Running".format(name=self.name))
            return {'status': 'success', 'current_state': KVM_Status.running}
        except Exception as e:
            kvm_log.error(" :: {name} :: Error Starting. Traceback : {e}".format(name=self.name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    def shutdown(self):
        if self.status is KVM_Status.rebooting:
            kvm_log.error(" :: {name} :: Already Stopped".format(name=self.name))
            return {'status': 'failed', 'reason': 'Already Stopped'}

        try:
            self.kvm.shutdown()
            kvm_log.debug(" :: {name} :: Shutdown Success.".format(name=self.name))
            return {'status': 'success', 'current_state': KVM_Status.stopped}
        except Exception as e:
            kvm_log.error(" :: {name} :: Error while shutting down. Traceback : {e}".format(name=self.name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    def stop(self):
        if self.status is KVM_Status.rebooting:
            kvm_log.error(" :: {name} :: Already Stopped".format(name=self.name))
            return {'status': 'failed', 'reason': 'Already Stopped'}

        try:
            self.kvm.destroy()
            kvm_log.debug(" :: {name} :: Stopping Success.".format(name=self.name))
            return {'status': 'success', 'current_state': KVM_Status.stopped}
        except Exception as e:
            kvm_log.error(" :: {name} :: Error while stopping. Traceback : {e}".format(name=self.name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    def suspend(self):
        if self.status is KVM_Status.suspended:
            kvm_log.error(" :: {name} :: Already suspended".format(name=self.name))
            return {'status': 'failed', 'reason': 'Already Suspended'}

        try:
            self.kvm.suspend()
            kvm_log.debug(" :: {name} :: Suspend Success.".format(name=self.name))
            return {'status': 'success', 'current_state': KVM_Status.suspended}
        except Exception as e:
            kvm_log.error(" :: {name} :: Error suspending down. Traceback : {e}".format(name=self.name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    def mainatain(self):
        resp = self.suspend()
        if resp['status'] == 'success':
            return {'status': 'success', 'current_state': KVM_Status.suspended}
        else:
            return resp

    def resume(self):
        if self.status is not KVM_Status.suspended:
            kvm_log.error(" :: {name} :: Tried resuming, state is not suspended.".format(name=self.name))
            return {'status': 'failed', 'reason': 'Not Suspended'}

        try:
            self.kvm.resume()
            kvm_log.debug(" :: {name} :: Resume success.".format(name=self.name))
            return {'status': 'success', 'current_state': KVM_Status.running}
        except Exception as e:
            kvm_log.error(" :: {name} :: Error resuming. Traceback : {e}".format(name=self.name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}
