"""
ccextractor-web | TestAuthentication.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import unittest
import time
from run import app
from tests.template_test_helper import captured_templates
from mod_auth.controller import generate_verification_code, send_verification_mail, send_signup_confirmation_mail


class TestEmailSignUp(unittest.TestCase):
    def setUp(self):
        pass

    def test_if_email_signup_form_renders(self):
        with captured_templates(app) as templates:
            response = app.test_client().get('/signup')
            self.assertEqual(response.status_code, 200)
            assert len(templates) == 1
            template, context = templates[0]
            assert template.name == 'mod_auth/signup.html'

    def test_blank_email(self):
        response = self.signup_email(email='')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address is not filled in', response.data)

    def test_invalid_email_address(self):
        invalid_email_address = ['plainaddress',
                                 '#@%^%#$@#$@#.com',
                                 '@domain.com',
                                 'Joe Smith <email@domain.com>',
                                 'email.domain.com',
                                 'email@domain.com (Joe Smith)',
                                 'email@domain',
                                 'email@-domain.com',
                                 'email@111.222.333.44444']

        for email in invalid_email_address:
            response = self.signup_email(email)
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                b'Entered value is not a valid email address.', response.data)

    def test_sending_verification_mail(self):
        with app.app_context():
            email = 'someone@example.com'
            expires = int(time.time()) + 86400
            verification_code = generate_verification_code(
                "{email}{expires}".format(email=email, expires=expires))
            response = send_verification_mail(
                email, verification_code, expires)
            self.assertEqual(response.status_code, 401)

    def signup_email(self, email):
        return app.test_client().post('/signup', data=dict(email=email), follow_redirects=True)


class TestVerify(unittest.TestCase):
    def setUp(self):
        pass

    def test_if_verifying_using_empty_information(self):
        response = app.test_client().get('/verify/')
        self.assertEqual(response.status_code, 404)

        response = app.test_client().get('/verify/email@email.com/')
        self.assertEqual(response.status_code, 404)

    def test_if_verification_link_expired(self):
        now = int(time.time())
        link_expired_at = now - 3600
        response = app.test_client().get(
            '/verify/someone@example.com/verificationcode/{expires}'.format(expires=link_expired_at), follow_redirects=True)
        self.assertIn(b'verification link is expired', response.data)

    def test_if_verification_unssuccessul(self):
        with app.app_context():
            email = 'someone@example.com'
            expires = int(time.time()) + 86400
            fake_expire = int(time.time()) + 3600
            verification_code = generate_verification_code(
                "{email}{expires}".format(email=email, expires=expires))

            response = app.test_client().get('/verify/{email}/{verification_code}/{expires}'.format(
                email='wrong@email.com', verification_code=verification_code, expires=expires), follow_redirects=True)
            self.assertIn(b'Verification failed!', response.data)

            response = app.test_client().get('/verify/{email}/{verification_code}/{expires}'.format(
                email=email, verification_code='wrong-code', expires=expires), follow_redirects=True)
            self.assertIn(b'Verification failed!', response.data)

            response = app.test_client().get('/verify/{email}/{verification_code}/{expires}'.format(
                email=email, verification_code=verification_code, expires=fake_expire), follow_redirects=True)
            self.assertIn(b'Verification failed!', response.data)

    def test_if_verification_successful(self):
        with app.app_context():
            email = 'someone@example.com'
            expires = int(time.time()) + 86400
            verification_code = generate_verification_code(
                "{email}{expires}".format(email=email, expires=expires))
            response = app.test_client().get('/verify/{email}/{verification_code}/{expires}'.format(
                email=email, verification_code=verification_code, expires=expires), follow_redirects=True)
            self.assertIn(b'Verification complete!', response.data)

    def test_sending_confirmation_mail(self):
        with app.app_context():
            email = 'someone@example.com'
            response = send_signup_confirmation_mail(email)
            self.assertEqual(response.status_code, 401)


class TestLogIn(unittest.TestCase):
    def setUp(self):
        pass

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

    def test_blank_password(self):

        response = self.login(email='someone@example.com', password='')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password cannot be empty.', response.data)

    def login(self, email, password, submit='Login'):
        return app.test_client().post('/login', data=dict(email=email,
                                                          password=password, submit=submit), follow_redirects=True)


class TestProfile(unittest.TestCase):
    def setUp(self):
        pass

    def test_if_access_denied_without_login(self):
        response = app.test_client().get('/profile')
        self.assertEqual(response.status_code, 302)

    def test_if_without_login_redirected_to_login_page(self):
        response = app.test_client().get('/profile')
        self.assertIn(
            b'<a href="/login?next=mod_auth.profile">/login?next=mod_auth.profile</a>', response.data)


def login_helper(client, email, password, submit='Login'):
    return client.post('/login', data=dict(email=email,
                                           password=password, submit=submit), follow_redirects=True)


class TestUsersAdmin(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_CHECK_DEFAULT'] = False
        pass

    def test_can_access_users_list_page(self):
        client = app.test_client()
        login_helper(
            client, app.config['ADMIN_EMAIL'], app.config['ADMIN_PWD'])

        response = client.get("/admin-dashboard/users")
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'id="dataTable"', response.data)
        self.assertIn(b'<th>Account Type</th>', response.data)

    def test_if_without_login_redirected_to_login_page(self):
        client = app.test_client()

        response = client.get("/admin-dashboard/users")
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            b'<a href="/login?next=mod_dashboard.user_list">/login?next=mod_dashboard.user_list</a>', response.data)


class TestFilesAdmin(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        pass

    def test_can_access_uploaded_files_list_page(self):
        client = app.test_client()
        login_helper(client, app.config['ADMIN_EMAIL'], app.config['ADMIN_PWD'])

        response = client.get("/admin-dashboard/files")
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'id="dataTable"', response.data)
        self.assertIn(b'<th>User ID</th>', response.data)

    def test_if_without_login_redirected_to_login_page(self):
        client = app.test_client()

        response = client.get("/admin-dashboard/files")
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            b'<a href="/login?next=mod_dashboard.admin_uploaded_files">/login?next=mod_dashboard.admin_uploaded_files</a>', response.data)


class TestErrorHandlers(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        pass

    def test_404_page_is_shown(self):
        client = app.test_client()
        response = client.get("/i-dont-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            b'<h1>Error 404 - Page not found</h1>', response.data)

    def test_404_page_with_dashboard_links_is_shown_when_logged_in(self):
        client = app.test_client()
        login_helper(
            client, app.config['ADMIN_EMAIL'], app.config['ADMIN_PWD'])
        response = client.get("/i-dont-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            b'data-target="#logoutModal"', response.data)
