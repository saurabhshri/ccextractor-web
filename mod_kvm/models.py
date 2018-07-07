"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from database import db
from datetime import datetime
import enum
import libvirt

from mod_dashboard.models import Platforms

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
        pass


def kvm_manager(name, op=None):
    status = KVM_Status.unknown
    conn = libvirt.open("qemu:///system")
    if conn is None:
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
            return {'status': 'already_running'}

        try:
            kvm.create()
            print(" : {name} : Started Running".format(name=name))
            return {'status': 'success'}
        except Exception as e:
            print(" : {name} : Error Starting. Traceback : {e}".format(name=name, e=e))
            return {'status': 'failed'}

    if op is KVM_cmds.stop or op is KVM_cmds.shutdown:
        if status is KVM_Status.stopped or status is KVM_Status.rebooting:
            print(" : {name} : Already Stopped".format(name=name))
            return {'status': 'already_stopped'}

        try:
            if op is KVM_cmds.shutdown:
                kvm.shutdown()
            elif op is KVM_cmds.stop:
                kvm.destroy()
            print(" : {name} : {cmd} success.".format(name=name, cmd=op.value))
            return {'status': 'success'}
        except Exception as e:
            print(" : {name} : {cmd} error. Traceback : {e}".format(name=name, cmd=op.value, e=e))
            return {'status': 'failed'}

    if op is KVM_cmds.suspend:
        if status is KVM_Status.suspended:
            print(" : {name} : Already suspended".format(name=name))
            return {'status': 'already_suspended'}

        try:
            kvm.suspend()
            print(" : {name} : {cmd} success.".format(name=name, cmd=op.value))
            return {'status': 'success'}
        except Exception as e:
            print(" : {name} : {cmd} error. Traceback : {e}".format(name=name, cmd=op.value, e=e))
            return {'status': 'failed'}

    conn.close()
