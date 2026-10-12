from core.models import Comment

from .base import BaseTest


class InteractionTests(BaseTest):
    def setUp(self):
        self.me = self.make_user("ana")
        self.bob = self.make_user("bob")
        self.post = self.make_post(self.bob)
        self.url = f"/api/posts/{self.post.id}/"
        self.login(self.me)

    def test_01_like_post(self):
        r = self.client.post(self.url + "like/")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["likes_count"], 1)

    def test_02_like_twice_counts_once(self):
        self.client.post(self.url + "like/")
        r = self.client.post(self.url + "like/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["likes_count"], 1)

    def test_03_unlike_post(self):
        self.client.post(self.url + "like/")
        r = self.client.delete(self.url + "like/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["likes_count"], 0)

    def test_04_liked_by_me_flag(self):
        self.assertFalse(self.client.get(self.url).data["liked_by_me"])
        self.client.post(self.url + "like/")
        self.assertTrue(self.client.get(self.url).data["liked_by_me"])

    def test_05_create_comment(self):
        r = self.client.post(self.url + "comments/", {"content": "Boa!"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["user"]["username"], "ana")
        self.assertEqual(self.client.get(self.url).data["comments_count"], 1)

    def test_06_empty_comment_fails(self):
        r = self.client.post(self.url + "comments/", {"content": ""}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_07_list_comments(self):
        Comment.objects.create(user=self.bob, post=self.post, content="um")
        Comment.objects.create(user=self.me, post=self.post, content="dois")
        r = self.client.get(self.url + "comments/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c["content"] for c in r.data["results"]], ["um", "dois"])

    def test_08_only_author_deletes_comment(self):
        c = Comment.objects.create(user=self.bob, post=self.post, content="meu")
        self.assertEqual(self.client.delete(f"/api/comments/{c.id}/").status_code, 403)
        self.client.force_authenticate(self.bob)
        self.assertEqual(self.client.delete(f"/api/comments/{c.id}/").status_code, 204)
