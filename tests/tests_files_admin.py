import unittest
import time
from run import app
from tests.template_test_helper import captured_templates
from tests.auth_utils import login


class TestFilesAdmin(unittest.TestCase):
    def setUp(self):
        pass

    def test_can_access_uploaded_files_list_page(self):
        client = app.test_client()
        login(client, app.config['ADMIN_EMAIL'], app.config['ADMIN_PWD'])

        response = client.get("/admin-dashboard/files")
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(b'id="dataTable"', response.data)
        self.assertIn(b'Uploaded Files', response.data)

    def test_if_without_login_redirected_to_login_page(self):
        client = app.test_client()

        response = client.get("/admin-dashboard/files")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'<a href="/login?next=mod_dashboard.admin_uploaded_files">/login?next=mod_dashboard.admin_uploaded_files</a>', response.data)
