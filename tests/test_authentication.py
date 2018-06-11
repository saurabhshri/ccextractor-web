"""
ccextractor-web | TestAuthentication.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest
from run import app, createConfig
from tests.template_test_helper import captured_templates

class TestSignUp(unittest.TestCase):
    def setUp(self):
        createConfig()

    def test_if_signup_form_renders(self):
        with captured_templates(app) as templates:
            response = app.test_client().get('/signup')
            self.assertEqual(response.status_code, 200)
            assert len(templates) == 1
            template, context = templates[0]
            assert template.name == 'mod_auth/signup.html'

    def test_blank_email(self):

        response = self.signup(name='Valid Name',
                                 email = '',
                                 password='somepassword',
                                 password_repeat='differentpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address is not filled in', response.data)


    def test_invalid_email_address(self):

        invalid_email_address = ['plainaddress',
                                 '#@%^%#$@#$@#.com',
                                 '@domain.com',
                                 'Joe Smith <email@domain.com>',
                                 'email.domain.com',
                                 'mail@domain@domain.com',
                                 '.email@domain.com',
                                 'email.@domain.com',
                                 'email..email@domain.com',
                                 'email@domain.com (Joe Smith)',
                                 'email@domain',
                                 'email@-domain.com',
                                 'email@domain.web',
                                 'email@111.222.333.44444',
                                 'email@domain..com']

        for email in invalid_email_address:
            response = self.signup(name='Valid Name',
                                   email=email,
                                   password='somepassword',
                                   password_repeat='somepassword')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Entered value is not a valid email address.', response.data)

    def test_blank_password(self):

        response = self.signup(name='Valid Name',
                                 email = 'someone@example.com',
                                 password='',
                                 password_repeat='')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password is not filled in.', response.data)
        self.assertIn(b'Repeated password is not filled in.', response.data)

    def test_repeat_password_not_matching(self):

        response = self.signup(name='Valid Name',
                                 email='someone@example.com',
                                 password='somepassword',
                                 password_repeat='differentpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The password needs to match the new password.', response.data)

    def signup(self, name, email, password, password_repeat):
        return app.test_client().post('/signup', data=dict(name=name,
                                                           email=email,
                                                           password=password,
                                                           password_repeat=password_repeat), follow_redirects=True)

class TestLogIn(unittest.TestCase):
    def setUp(self):
        createConfig()

    def test_if_login_form_renders(self):
        with captured_templates(app) as templates:
            response = app.test_client().get('/login')
            self.assertEqual(response.status_code, 200)
            assert len(templates) == 1
            template, context = templates[0]
            assert template.name == 'mod_auth/login.html'

    def test_blank_email(self):

        response = self.login(email='', password='somepassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address is not filled in.', response.data)


    def test_invalid_email_address(self):

        response = self.login(email='invalid&&email@something@.com', password='somepassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Entered value is not a valid email address.', response.data)

    def test_blank_password(self):

        response = self.login(email = 'someone@example.com', password='')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password cannot be empty.', response.data)

    def login(self, email, password, submit='Login'):
        return app.test_client().post('/login', data=dict(email=email,
                                                          password=password, submit=submit), follow_redirects=True)

class TestLogOut(unittest.TestCase):
    def setUp(self):
        createConfig()

    def test_if_logout_redirects_to_login(self):
        response = app.test_client().get('/logout')
        self.assertEqual(response.status_code, 302)

class TestProfile(unittest.TestCase):
    def setUp(self):
        createConfig()

    def test_if_access_denied_without_login(self):
        response = app.test_client().get('/profile')
        self.assertEqual(response.status_code, 302)

    def test_if_without_login_redirected_to_login_page(self):
        response = app.test_client().get('/profile')
        self.assertIn(b'<a href="/login?next=mod_auth.profile">/login?next=mod_auth.profile</a>', response.data)
