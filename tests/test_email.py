"""
ccextractor-web | mod_auth/controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest

from run import app
from mail import send_simple_message, get_api_url


class TestEmail(unittest.TestCase):
    def setUp(self):
        pass

    def test_if_correct_api_url_is_generated(self):
        obtained_api_url = get_api_url(app.config['EMAIL_DOMAIN'])
        expected_api_url = 'https://api.mailgun.net/v3/xxxxx.mailgun.org/messages'
        self.assertEqual(expected_api_url, obtained_api_url)

    def test_sending_email_with_invalid_config(self):
        with app.app_context():
            response = send_simple_message('mail@example.com', 'This will fail', 'This will fail')
            self.assertEqual(response.status_code, 401)
