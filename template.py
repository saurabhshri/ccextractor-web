"""
ccextractor-web | template.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
from datetime import datetime, timezone


class LayoutHelper():
    def __init__(self, logged_in):
        self.entries = {}
        self.entries['logged_in'] = "false"

        if logged_in:
            self.entries['menu'] = [
                {
                    'display_name': 'Dashboard',
                    'url': 'dashboard',
                    'icon': 'fa fa-fw fa-dashboard'
                },
                {
                    'display_name': 'Files',
                    'url': 'files',
                    'icon': 'fa fa-fw fa-file'
                },
                {
                    'display_name': 'Queue',
                    'url': 'queue',
                    'icon': 'fa fa-fw fa-spinner'
                }
            ]
            self.entries['logged_in'] = "true"

        else:
            self.entries['menu'] = [
                {
                    'display_name': 'Login',
                    'url': 'login',
                    'icon': 'fa fa-fw fa-user'
                },
                {
                    'display_name': 'SignUp',
                    'url': 'signup',
                    'icon': 'fa fa-fw fa-pen'
                }
            ]

        now = datetime.now(timezone.utc)
        self.entries['year'] = now.year
        self.entries['curr_time'] = now

    def get_entries(self):
        return self.entries
