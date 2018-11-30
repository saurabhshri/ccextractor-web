from flask import Blueprint, g, render_template
from template import LayoutHelper

from mod_landing.models import LandingPageStatistics
from mod_dashboard.models import DetailsForTemplate

mod_landing = Blueprint("mod_landing", __name__)


@mod_landing.route('/')
def index():
    layout = LayoutHelper(logged_in=False)
    details = None
    statistics = LandingPageStatistics()

    try:
        if g.user is not None:
            details = DetailsForTemplate(g.user.id)
            layout = LayoutHelper(logged_in=True, details=details)

    except Exception:
        pass

    return render_template("mod_landing/landing.html", layout=layout.get_entries(), statistics=statistics, details=details)
