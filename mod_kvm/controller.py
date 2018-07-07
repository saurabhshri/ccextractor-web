"""
ccextractor-web | controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
import datetime

from database import db

from mod_auth.controller import login_required, check_account_type
from mod_auth.models import AccountType
from mod_kvm.models import KVM, VM, kvm_manager, KVM_Status
from mod_dashboard.models import Platforms

mod_kvm = Blueprint("mod_kvm", __name__)

def init_kvm_db():
    from flask import current_app as app

    for platform in Platforms:
        name = app.config['KVM_{platform}_NAME'.format(platform=platform.value.upper())]
        kvm = KVM.query.filter(KVM.name == name).first()
        if kvm is None:
            status = kvm_manager(name)
            kvm = KVM(name=name, platform=platform.value, status=status, timestamp=datetime.datetime.now())
            db.session.add(kvm)
            db.session.commit()

@mod_kvm.route('/kvm', methods=['GET', 'POST'])
@login_required
@check_account_type([AccountType.admin])
def manage_kvm():
    kvm = KVM.query.all()
    return render_template('mod_kvm/kvm.html', kvm=kvm, kvm_status=KVM_Status)

@mod_kvm.route('/kvm-cmd/<cmd>/<kvm_name>', methods=['GET', 'POST'])
@login_required
@check_account_type([AccountType.admin])
def kvm_cmd(cmd, kvm_name):
    vm = VM(kvm_name)

    if cmd == 'start':
       vm.start()

    elif cmd == 'stop':
        vm.stop()

    if cmd == 'shutdown':
        vm.shutdown()

    return redirect(url_for('mod_kvm.manage_kvm'))



