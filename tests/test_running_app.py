"""
ccextractor-web | TestRunningApp.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest

from run import app, init_app
from mod_auth.models import AccountType, Users


class TestRunningApp(unittest.TestCase):
    def create_app(self):
        app.run()

    def test_flask_application_is_up_and_running(self):
        response = app.test_client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_added(self):
        """
        Test that an admin user is created on initializing app
        """
        with app.app_context():
            app.config['ADMIN_EMAIL'] = 'something_random@gmail.com'
            init_app()
            user = Users.query.filter(Users.account_type == AccountType.admin).first()
            self.assertNotEqual(user, None)
