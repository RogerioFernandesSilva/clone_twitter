from .base import BaseTest


class FollowTests(BaseTest):
    def setUp(self):
        self.me = self.make_user("ana")
        self.bob = self.make_user("bob")
        self.login(self.me)

    def test_01_follow_user(self):
        r = self.client.post("/api/users/bob/follow/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["is_following"])
        self.assertEqual(r.data["followers_count"], 1)
        self.assertIn(self.bob, self.me.following.all())

    def test_02_cannot_follow_self(self):
        self.assertEqual(self.client.post("/api/users/ana/follow/").status_code, 400)

    def test_03_follow_nonexistent_user(self):
        self.assertEqual(self.client.post("/api/users/fantasma/follow/").status_code, 404)

    def test_04_unfollow_user(self):
        self.me.following.add(self.bob)
        r = self.client.delete("/api/users/bob/follow/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["is_following"])
        self.assertEqual(self.me.following.count(), 0)

    def test_05_follow_twice_is_idempotent(self):
        self.client.post("/api/users/bob/follow/")
        self.client.post("/api/users/bob/follow/")
        self.assertEqual(self.me.following.count(), 1)

    def test_06_followers_list(self):
        self.me.following.add(self.bob)
        r = self.client.get("/api/users/bob/followers/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([u["username"] for u in r.data["results"]], ["ana"])

    def test_07_following_list(self):
        self.me.following.add(self.bob)
        r = self.client.get("/api/users/ana/following/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([u["username"] for u in r.data["results"]], ["bob"])

    def test_08_follow_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post("/api/users/bob/follow/").status_code, 401)
