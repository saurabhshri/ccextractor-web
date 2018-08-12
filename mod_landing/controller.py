from flask import Blueprint, g, redirect, url_for

mod_landing = Blueprint("mod_landing", __name__)

@mod_landing.route('/')
def index():
    try:
        if g.user is not None:
            return redirect(url_for('mod_dashboard.dashboard'))

    except Exception as e:
        return redirect(url_for('mod_auth.login'))

    return redirect(url_for('mod_auth.login'))
