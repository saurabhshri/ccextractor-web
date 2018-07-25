"""
ccextractor-web | template.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
from datetime import datetime, timezone
from flask import url_for


class LayoutHelper():
    def __init__(self, logged_in, admin=False):
        self.entries = {}
        self.entries['logged_in'] = "false"

        if logged_in and admin:
            self.entries['menu'] = [
                {
                    'display_name': 'Dashboard',
                    'url': url_for('mod_dashboard.admin'),
                    'icon': 'fa fa-fw fa-dashboard'
                },
                {
                    'display_name': 'Files',
                    'url': url_for('mod_dashboard.admin_uploaded_files'),
                    'icon': 'fa fa-fw fa-file'
                },
                {
                    'display_name': 'Queue',
                    'url': url_for('mod_dashboard.admin_queue'),
                    'icon': 'fa fa-fw fa-spinner'
                }
            ]
            self.entries['logged_in'] = "true"

        elif logged_in and not admin:
            self.entries['menu'] = [
                {
                    'display_name': 'Dashboard',
                    'url': url_for('mod_dashboard.dashboard'),
                    'icon': 'fa fa-fw fa-dashboard'
                },
                {
                    'display_name': 'Files',
                    'url': url_for('mod_dashboard.uploaded_files'),
                    'icon': 'fa fa-fw fa-file'
                },
                {
                    'display_name': 'Queue',
                    'url': url_for('mod_dashboard.user_queue'),
                    'icon': 'fa fa-fw fa-spinner'
                }
            ]
            self.entries['logged_in'] = "true"

        else:
            self.entries['menu'] = [
                {
                    'display_name': 'Login',
                    'url': url_for('mod_auth.login'),
                    'icon': 'fa fa-fw fa-sign-in'
                },
                {
                    'display_name': 'SignUp',
                    'url': 'signup',
                    'icon': 'fa fa-user-plus'
                }
            ]

        now = datetime.now(timezone.utc)
        self.entries['year'] = now.year
        self.entries['curr_time'] = now

    def get_entries(self):
        return self.entries
