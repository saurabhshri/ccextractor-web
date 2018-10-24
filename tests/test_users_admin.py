import unittest
import time
from run import app
from tests.template_test_helper import captured_templates
from tests.auth_utils import login


class TestUsersAdmin(unittest.TestCase):
    def setUp(self):
        pass

    def test_can_access_users_list_page(self):
        client = app.test_client()
        login(client, app.config['ADMIN_EMAIL'], app.config['ADMIN_PWD'])

        response = client.get("/admin-dashboard/users")
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(b'id="dataTable"', response.data)

    def test_if_without_login_redirected_to_login_page(self):
        client = app.test_client()

        response = client.get("/admin-dashboard/users")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'<a href="/login?next=mod_dashboard.user_list">/login?next=mod_dashboard.user_list</a>', response.data)
