"""
ccextractor-web | TestRunningApp.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54@gmail.com
Link     : https://github.com/saurabhshr

"""
import unittest, requests

from run import app, createConfig

class TestRunningApp(unittest.TestCase):
    def create_app(self):
        createConfig()
        app.run()

    def test_flask_application_is_up_and_running(self):
        response = app.test_client().get('/')
        self.assertEqual(response.status_code, 200)
