from flask import Blueprint, g, redirect, url_for, render_template
from template import LayoutHelper

mod_landing = Blueprint("mod_landing", __name__)

from mod_landing.models import LandingPageStatistics

@mod_landing.route('/')
def index():
    layout = LayoutHelper(logged_in = False)

    # Displaying statistics - might be insecure?
    statistics = LandingPageStatistics()

    try:
        if g.user is not None:
            return redirect(url_for('mod_dashboard.dashboard'))

    except Exception as e:
        return render_template("mod_landing/landing.html", layout = layout.get_entries(), statistics = statistics)

    return render_template("mod_landing/landing.html", layout = layout.get_entries(), statistics = statistics)
