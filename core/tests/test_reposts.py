from core.models import Post

from .base import BaseTest


class RepostTests(BaseTest):
    def setUp(self):
        self.me = self.make_user("ana")
        self.bob = self.make_user("bob")
        self.post = self.make_post(self.bob, "original")
        self.url = f"/api/posts/{self.post.id}/repost/"
        self.login(self.me)

    def test_01_repost(self):
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["repost_of"]["id"], self.post.id)
        self.assertEqual(r.data["author"]["username"], "ana")

    def test_02_cannot_repost_twice(self):
        self.client.post(self.url)
        self.assertEqual(self.client.post(self.url).status_code, 400)

    def test_03_repost_of_repost_points_to_original(self):
        rp = Post.objects.create(author=self.bob, repost_of=self.post)
        r = self.client.post(f"/api/posts/{rp.id}/repost/")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["repost_of"]["id"], self.post.id)

    def test_04_reposts_count(self):
        self.client.post(self.url)
        self.assertEqual(self.client.get(f"/api/posts/{self.post.id}/").data["reposts_count"], 1)

    def test_05_repost_nonexistent_post(self):
        self.assertEqual(self.client.post("/api/posts/9999/repost/").status_code, 404)

    def test_06_repost_cannot_be_edited(self):
        rp = Post.objects.create(author=self.me, repost_of=self.post)
        r = self.client.patch(f"/api/posts/{rp.id}/", {"content": "x"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_07_delete_own_repost(self):
        rp = Post.objects.create(author=self.me, repost_of=self.post)
        self.assertEqual(self.client.delete(f"/api/posts/{rp.id}/").status_code, 204)
        self.assertTrue(Post.objects.filter(pk=self.post.id).exists())

    def test_08_repost_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post(self.url).status_code, 401)
