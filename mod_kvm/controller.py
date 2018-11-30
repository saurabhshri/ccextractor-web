"""
ccextractor-web | controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import datetime
import json

from flask import Blueprint, flash, redirect, url_for

from database import db

from mod_auth.controller import login_required, check_account_type
from mod_auth.models import AccountType
from mod_kvm.models import KVM, VM, kvm_log
from mod_dashboard.models import Platforms


mod_kvm = Blueprint("mod_kvm", __name__)


def init_kvm_db():
    from flask import current_app as app

    for platform in Platforms:
        name = app.config['KVM_{platform}_NAME'.format(platform=platform.value.upper())]
        if name:
            kvm_log.debug('KVM : {name} > Trying to initialise.'.format(name=name))
            kvm = KVM.query.filter(KVM.name == name).first()
            if kvm is None:
                try:
                    vm = VM(name)
                except Exception as e:
                    kvm_log.error('KVM : {name} > Failed. Reason : {e}'.format(name=name, e=e))
                else:
                    status = vm.status
                    kvm_log.debug('KVM : {name} > Fetched status = {status}'.format(name=name, status=status))
                    kvm = KVM(name=name, platform=platform.value, status=status, timestamp=datetime.datetime.now())
                    db.session.add(kvm)
                    db.session.commit()
                    kvm_log.debug('KVM : {name} > Status updated in DB.'.format(name=name, status=status))
            else:
                kvm_log.warning('KVM : {name} > Already initialised.'.format(name=name))
                update_kvm_status(kvm_name=name)


@mod_kvm.route('/kvm-cmd/<cmd>/<kvm_name>', methods=['GET', 'POST'])
@login_required
@check_account_type([AccountType.admin])
def kvm_cmd(cmd, kvm_name):
    kvm = KVM.query.filter(KVM.name == kvm_name).first()
    if kvm is None:
        resp = {'status': 'failed', 'reason': '{KVM} not found'.format(KVM=kvm_name)}
        flash('Failed to execute {cmd} on KVM {kvm_name}, {reason}.'.format(cmd=cmd, kvm_name=kvm_name, reason=resp['reason']), 'error')

    else:
        try:
            vm = VM(kvm_name)
        except Exception as e:
            kvm_log.error('KVM : {name} > Failed. Reason : {e}'.format(name=kvm.name, e=e))
            resp = {'status': 'failed', 'reason': '{e}'.format(e=e)}
        else:
            if cmd == 'start':
                resp = vm.start()

            elif cmd == 'stop':
                resp = vm.stop()

            elif cmd == 'shutdown':
                resp = vm.shutdown()

            elif cmd == 'maintain':
                resp = vm.mainatain()

            elif cmd == 'resume':
                resp = vm.resume()

            else:
                resp = {'status': 'failed', 'reason': 'Command {cmd} not found'.format(cmd=cmd)}
                flash('Failed to execute {cmd} on KVM {kvm_name}, {reason}.'.format(cmd=cmd, kvm_name=kvm_name, reason=resp['reason']), 'error')

    if resp['status'] == 'success':
        kvm.status = resp['current_state']
        db.session.commit()
        flash('Executed {cmd} on KVM {kvm_name}.'.format(cmd=cmd, kvm_name=kvm_name), 'success')
    else:
        flash('Failed to execute {cmd} on KVM {kvm_name}, {reason}.'.format(cmd=cmd, kvm_name=kvm_name, reason=resp['reason']), 'error')

    return redirect(url_for('mod_dashboard.admin'))


@mod_kvm.route('/kvm-status/<kvm_name>', methods=['GET', 'POST'])
@login_required
@check_account_type([AccountType.admin])
def check_kvm_status(kvm_name):

    resp = json.loads(update_kvm_status(kvm_name=kvm_name))
    if resp['status'] == 'success':
        flash('Refreshed KVM {kvm_name}.'.format(kvm_name=kvm_name), 'success')
    else:
        flash('Failed to refresh KVM {kvm_name}, {reason}.'.format(kvm_name=kvm_name, reason=resp['reason']), 'error')

    return redirect(url_for('mod_dashboard.admin'))


def update_kvm_status(kvm_name):
    kvm = KVM.query.filter(KVM.name == kvm_name).first()
    if kvm is None:
        resp = {'status': 'failed', 'reason': '{KVM} not found'.format(KVM=kvm_name)}
    else:
        try:
            vm = VM(kvm_name)

        except Exception as e:
            kvm_log.error('KVM : {name} > Failed. Reason : {e}'.format(name=kvm.name, e=e))
            resp = {'status': 'failed', 'reason': '{e}'.format(e=e)}

        else:
            kvm_log.debug('KVM : {name} > Fetching status, current status in db : {status}'.format(name=kvm.name, status=kvm.status))
            try:
                status = vm.status
                kvm_log.debug('KVM : {name} > Fetching status, actual status : {status}'.format(name=kvm.name, status=status))
            except Exception as e:
                kvm_log.error('KVM : {name} > Failed to fetch status, {e}'.format(name=kvm.name, e=e))
                resp = {'status': 'failed', 'reason': '{e}'.format(e=e)}
            else:
                kvm.status = status
                db.session.commit()
                kvm_log.debug('KVM : {name} > Status in db updated.'.format(name=kvm.name, status=status))
                resp = {'status': 'success', 'state': '{state}'.format(state=kvm.status)}

    resp = json.dumps(resp)
    return resp
