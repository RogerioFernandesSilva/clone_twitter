from core.models import Post

from .base import BaseTest

FEED = "/api/feed/"


class FeedTests(BaseTest):
    def setUp(self):
        self.me = self.make_user("ana")
        self.bob = self.make_user("bob")
        self.cat = self.make_user("cat")
        self.login(self.me)

    def contents(self):
        return [p["content"] for p in self.client.get(FEED).data["results"]]

    def test_01_empty_feed_when_following_nobody(self):
        self.make_post(self.bob)
        r = self.client.get(FEED)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 0)

    def test_02_feed_shows_followed_posts(self):
        self.me.following.add(self.bob)
        self.make_post(self.bob, "do bob")
        self.assertEqual(self.contents(), ["do bob"])

    def test_03_feed_excludes_not_followed(self):
        self.me.following.add(self.bob)
        self.make_post(self.cat, "da cat")
        self.assertEqual(self.contents(), [])

    def test_04_feed_excludes_own_posts(self):
        self.me.following.add(self.bob)
        self.make_post(self.me, "meu")
        self.assertEqual(self.contents(), [])

    def test_05_feed_newest_first(self):
        self.me.following.add(self.bob)
        self.make_post(self.bob, "primeiro")
        self.make_post(self.bob, "segundo")
        self.assertEqual(self.contents(), ["segundo", "primeiro"])

    def test_06_feed_includes_reposts_of_followed(self):
        self.me.following.add(self.bob)
        original = self.make_post(self.cat, "da cat")
        Post.objects.create(author=self.bob, repost_of=original)
        results = self.client.get(FEED).data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["repost_of"]["content"], "da cat")

    def test_07_unfollow_removes_posts_from_feed(self):
        self.me.following.add(self.bob)
        self.make_post(self.bob)
        self.client.delete("/api/users/bob/follow/")
        self.assertEqual(self.contents(), [])

    def test_08_feed_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(FEED).status_code, 401)
