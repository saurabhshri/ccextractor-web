"""
ccextractor-web | template.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
from datetime import datetime, timezone
from flask import url_for


class LayoutHelper():
    def __init__(self, logged_in, details=None, admin=False):
        self.entries = {}
        self.entries['logged_in'] = "false"

        if logged_in:
            self.entries['logged_in'] = "true"
            self.entries['menu'] = [
                {
                    'display_name': 'Dashboard',
                    'url': details.dashboard_url,
                    'icon': 'fa fa-fw fa-dashboard'
                },
                {
                    'display_name': 'Files',
                    'url': details.uploaded_files_url,
                    'icon': 'fa fa-fw fa-file'
                },
                {
                    'display_name': 'Queue',
                    'url': details.queue_url,
                    'icon': 'fa fa-fw fa-spinner'
                }
            ]

            if details.admin_dashboard:
                try:
                    if details.user_dashboard_url:
                        self.entries['menu'].append(
                            {
                                'display_name': 'User List',
                                'url': details.user_list_url,
                                'icon': 'fa fa-fw fa-list'
                            })
                        self.entries['menu'].append(
                            {
                                'display_name': 'User Dashboard',
                                'url': details.user_dashboard_url,
                                'icon': 'fa fa-fw fa-user'
                            })
                except AttributeError:
                    pass

            else:
                try:
                    if details.admin_dashboard_url:
                        self.entries['menu'].append(
                            {
                                'display_name': 'Admin Dashboard',
                                'url': details.admin_dashboard_url,
                                'icon': 'fa fa-fw fa-lock'
                            })
                except AttributeError:
                    pass

        else:
            self.entries['menu'] = [
                {
                    'display_name': 'Home',
                    'url': url_for('mod_landing.index'),
                    'icon': 'fa fa-fw fa-home'
                },
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
