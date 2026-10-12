from core.models import Post

from .base import BaseTest

URL = "/api/posts/"


class PostTests(BaseTest):
    def setUp(self):
        self.me = self.make_user("ana")
        self.bob = self.make_user("bob")
        self.login(self.me)

    def test_01_create_post(self):
        r = self.client.post(URL, {"content": "Meu primeiro tweet"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["author"]["username"], "ana")

    def test_02_create_empty_post_fails(self):
        self.assertEqual(self.client.post(URL, {"content": ""}, format="json").status_code, 400)

    def test_03_create_post_over_280_chars_fails(self):
        r = self.client.post(URL, {"content": "x" * 281}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_04_list_posts(self):
        self.make_post(self.me)
        self.make_post(self.bob)
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)

    def test_05_retrieve_post(self):
        p = self.make_post(self.bob, "olha isso")
        r = self.client.get(f"{URL}{p.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["content"], "olha isso")

    def test_06_author_can_edit(self):
        p = self.make_post(self.me, "antes")
        r = self.client.patch(f"{URL}{p.id}/", {"content": "depois"}, format="json")
        self.assertEqual(r.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.content, "depois")

    def test_07_other_user_cannot_edit_or_delete(self):
        p = self.make_post(self.bob)
        self.assertEqual(self.client.patch(f"{URL}{p.id}/", {"content": "hack"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(f"{URL}{p.id}/").status_code, 403)
        self.assertTrue(Post.objects.filter(pk=p.id).exists())

    def test_08_author_can_delete(self):
        p = self.make_post(self.me)
        self.assertEqual(self.client.delete(f"{URL}{p.id}/").status_code, 204)
        self.assertFalse(Post.objects.filter(pk=p.id).exists())
