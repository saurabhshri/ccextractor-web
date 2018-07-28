"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from datetime import datetime
import enum
import libvirt

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
    reboot = 'reboot'
    maintain = 'maintain' #suspend + db shows maintainance

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
        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.start_timestamp = timestamp

    def __repr__(self):
        return '<KVM : {id}>'.format(id=self.id)

class VM():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<VM : {name}'.format(name=self.name)

    def status(self):
        return kvm_manager(self.name)

    def start(self):
        return kvm_manager(self.name, KVM_cmds.start)

    def shutdown(self):
        return kvm_manager(self.name, KVM_cmds.shutdown)

    def stop(self):
        return kvm_manager(self.name, KVM_cmds.stop)

    def suspend(self):
        return kvm_manager(self.name, KVM_cmds.suspend)

    def mainatain(self):
        return kvm_manager(self.name, KVM_cmds.maintain)


def kvm_manager(name, op=None):
    status = KVM_Status.unknown
    conn = libvirt.open("qemu:///system")
    if conn is None:
        kvm_log.debug("Couldn't open connection to libvirt!")
        print("Couldn't open connection to libvirt!")
        return None

    try:
        kvm = conn.lookupByName(name)
    except libvirt.libvirtError:
        print("Couldn't find KVM with name : {name}".format(name=name))
        status = KVM_Status.not_found
        return None

    state, reason =kvm.state()

    if state == libvirt.VIR_DOMAIN_RUNNING:
        status = KVM_Status.running
    elif state == libvirt.VIR_DOMAIN_PAUSED:
        status = KVM_Status.suspended
    elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
        status = KVM_Status.rebooting
    elif state == libvirt.VIR_DOMAIN_SHUTOFF:
        status = KVM_Status.stopped
    elif state == libvirt.VIR_DOMAIN_CRASHED:
        status = KVM_Status.crashed
    else:
        status = KVM_Status.unknown

    """
    if kvm.isActive():
        print(" : {name} : Found Running".format(name=name))
        status = KVM_Status.running
    else:
        print(" : {name} : Found Stopped".format(name=name))
        status = KVM_Status.stopped
    """

    if op is None:
        return status

    if op is KVM_cmds.start:
        if status is KVM_Status.running:
            print(" : {name} : Already Running".format(name=name))
            return {'status': 'failed', 'reason': 'Already Running'}

        try:
            kvm.create()
            print(" : {name} : Started Running".format(name=name))
            return {'status': 'success', 'new_state': KVM_Status.running}
        except Exception as e:
            print(" : {name} : Error Starting. Traceback : {e}".format(name=name, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    if op is KVM_cmds.stop or op is KVM_cmds.shutdown:
        if status is KVM_Status.stopped or status is KVM_Status.rebooting:
            print(" : {name} : Already Stopped".format(name=name))
            return {'status': 'failed', 'reason': 'Already Stopped'}

        try:
            if op is KVM_cmds.shutdown:
                kvm.shutdown()
                print(" : {name} : {cmd} success, new state = {new_state}".format(name=name, cmd=op.value, new_state=KVM_Status.rebooting))
                return {'status': 'success', 'new_state': KVM_Status.rebooting}
            elif op is KVM_cmds.stop:
                kvm.destroy()
                print(" : {name} : {cmd} success, new state = {new_state}".format(name=name, cmd=op.value, new_state=KVM_Status.stopped))
                return {'status': 'success', 'new_state': KVM_Status.stopped}
        except Exception as e:
            print(" : {name} : {cmd} error. Traceback : {e}".format(name=name, cmd=op.value, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    if op is KVM_cmds.suspend or op is KVM_cmds.maintain:
        if status is KVM_Status.suspended:
            print(" : {name} : Already suspended".format(name=name))
            return {'status': 'failed', 'reason': 'Already Suspended'}

        try:
            kvm.suspend()
            print(" : {name} : {cmd} success, new state = {new_state} ".format(name=name, cmd=op.value, new_state=KVM_Status.stopped))
            if op is KVM_cmds.suspend:
                return {'status': 'success', 'new_state': KVM_Status.suspended}
            elif op is KVM_cmds.maintain:
                return {'status': 'success', 'new_state': KVM_Status.maintainance}
        except Exception as e:
            print(" : {name} : {cmd} error. Traceback : {e}".format(name=name, cmd=op.value, e=e))
            return {'status': 'failed', 'reason': '{e}'.format(e=e)}

    conn.close()
