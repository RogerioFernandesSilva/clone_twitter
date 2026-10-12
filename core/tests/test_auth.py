from .base import BaseTest, PASSWORD

REGISTER = "/api/auth/register/"
LOGIN = "/api/auth/login/"


class AuthTests(BaseTest):
    def test_01_register_success(self):
        r = self.client.post(REGISTER, {"username": "ana", "name": "Ana", "password": PASSWORD})
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("password", r.data)
        self.assertEqual(r.data["name"], "Ana")

    def test_02_register_duplicate_username(self):
        self.make_user("ana")
        r = self.client.post(REGISTER, {"username": "ana", "password": PASSWORD})
        self.assertEqual(r.status_code, 400)

    def test_03_register_weak_password(self):
        r = self.client.post(REGISTER, {"username": "ana", "password": "123"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("password", r.data)

    def test_04_register_missing_username(self):
        r = self.client.post(REGISTER, {"password": PASSWORD})
        self.assertEqual(r.status_code, 400)

    def test_05_login_success_returns_tokens(self):
        self.make_user("ana")
        r = self.client.post(LOGIN, {"username": "ana", "password": PASSWORD})
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertIn("refresh", r.data)

    def test_06_login_wrong_password(self):
        self.make_user("ana")
        r = self.client.post(LOGIN, {"username": "ana", "password": "errada"})
        self.assertEqual(r.status_code, 401)

    def test_07_protected_route_without_token(self):
        self.assertEqual(self.client.get("/api/profile/").status_code, 401)

    def test_08_protected_route_with_token(self):
        self.make_user("ana")
        token = self.client.post(LOGIN, {"username": "ana", "password": PASSWORD}).data["access"]
        r = self.client.get("/api/profile/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "ana")
