"""
ccextractor-web | TestConfig.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest

from run import app


class TestConfig(unittest.TestCase):
    def setUp(self):
        pass

    def test_if_config_is_being_read(self):
        # config.py
        self.assertEqual(app.config['CONFIG_READING_TEST'], 'May the 24th be with you!')

        # instance/config.py
        self.assertEqual(app.config['SECRET_CONFIG_READING_TEST'], 'It\'s a magical place.')
