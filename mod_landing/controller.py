from flask import Blueprint, g, redirect, url_for, render_template
from template import LayoutHelper

mod_landing = Blueprint("mod_landing", __name__)

from mod_landing.models import LandingPageStatistics
from mod_dashboard.models import DetailsForTemplate

@mod_landing.route('/')
def index():
    layout = LayoutHelper(logged_in = False)
    details = None
    statistics = LandingPageStatistics()
    
    try:
        if g.user is not None:
            details = DetailsForTemplate(g.user.id)
            layout = LayoutHelper(logged_in = True, details = details)
    
    except Exception as e:
        pass
            
    return render_template("mod_landing/landing.html", layout = layout.get_entries(), statistics = statistics, details = details)
