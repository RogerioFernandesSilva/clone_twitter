import tempfile

from django.test import override_settings

from .base import BaseTest, PASSWORD, image_file

URL = "/api/profile/"
NEW_PW = "NovaSenha@789"


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProfileTests(BaseTest):
    def setUp(self):
        self.u = self.make_user("ana", first_name="Ana")
        self.login(self.u)

    def test_01_get_profile(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["name"], "Ana")

    def test_02_change_only_name(self):
        r = self.client.patch(URL, {"name": "Ana Maria"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.u.refresh_from_db()
        self.assertEqual(self.u.first_name, "Ana Maria")
        self.assertTrue(self.u.check_password(PASSWORD))
        self.assertFalse(self.u.avatar)

    def test_03_change_only_avatar(self):
        r = self.client.patch(URL, {"avatar": image_file()}, format="multipart")
        self.assertEqual(r.status_code, 200)
        self.u.refresh_from_db()
        self.assertTrue(self.u.avatar)
        self.assertEqual(self.u.first_name, "Ana")

    def test_04_change_only_password(self):
        r = self.client.patch(URL, {"current_password": PASSWORD, "password": NEW_PW}, format="json")
        self.assertEqual(r.status_code, 200)
        self.u.refresh_from_db()
        self.assertTrue(self.u.check_password(NEW_PW))

    def test_05_password_requires_current_password(self):
        r = self.client.patch(URL, {"password": NEW_PW}, format="json")
        self.assertEqual(r.status_code, 400)
        self.u.refresh_from_db()
        self.assertTrue(self.u.check_password(PASSWORD))

    def test_06_wrong_current_password(self):
        r = self.client.patch(URL, {"current_password": "errada", "password": NEW_PW}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("current_password", r.data)

    def test_07_empty_patch_changes_nothing(self):
        r = self.client.patch(URL, {}, format="json")
        self.assertEqual(r.status_code, 200)
        self.u.refresh_from_db()
        self.assertEqual(self.u.first_name, "Ana")
        self.assertTrue(self.u.check_password(PASSWORD))

    def test_08_change_everything_at_once(self):
        r = self.client.patch(URL, {"name": "Novo", "avatar": image_file(),
                                    "current_password": PASSWORD, "password": NEW_PW},
                              format="multipart")
        self.assertEqual(r.status_code, 200)
        self.u.refresh_from_db()
        self.assertEqual(self.u.first_name, "Novo")
        self.assertTrue(self.u.avatar)
        self.assertTrue(self.u.check_password(NEW_PW))
