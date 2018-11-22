from flask import Blueprint, g, redirect, url_for, render_template
from template import LayoutHelper

mod_landing = Blueprint("mod_landing", __name__)

@mod_landing.route('/')
def index():
    layout = LayoutHelper(logged_in = False)

    try:
        if g.user is not None:
            return redirect(url_for('mod_dashboard.dashboard'))

    except Exception as e:
        return render_template("mod_landing/landing.html", layout = layout.get_entries())

    return render_template("mod_landing/landing.html", layout = layout.get_entries())
