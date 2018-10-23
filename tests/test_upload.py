"""
ccextractor-web | TestUpload.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest
from run import app


class TestUpload(unittest.TestCase):

    def setUp(self):
        pass

    def test_if_without_login_redirected_to_login_page(self):
        response = app.test_client().get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'<a href="/login?next=mod_dashboard.dashboard">/login?next=mod_dashboard.dashboard</a>', response.data)
