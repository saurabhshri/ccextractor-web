"""
ccextractor-web | TestConfig.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54@gmail.com
Link     : https://github.com/saurabhshr

"""
import unittest

from run import app, createConfig

class TestConfig(unittest.TestCase):
    def test_if_config_is_being_read(self):
        createConfig()

        #config.py
        self.assertEqual(app.config['CONFIG_READING_TEST'], 'May the 24th be with you!')

        #instance/config.py
        self.assertEqual(app.config['SECRET_CONFIG_READING_TEST'], 'Its a magical place.')
