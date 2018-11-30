"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from mod_dashboard.models import ProcessQueue, ProcessStauts
from mod_auth.models import Users


class LandingPageStatistics():
    user_count = 0
    files_pending_count = 0
    files_completed_count = 0

    def __init__(self):
        self.user_count = len(Users.query.all())
        self.files_pending_count = len(ProcessQueue.query.filter((ProcessQueue.status == ProcessStauts.pending)).all())
        self.files_completed_count = len(ProcessQueue.query.filter((ProcessQueue.status == ProcessStauts.completed)).all())
