from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """first_name é usado como 'nome de exibição'."""
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )


class Post(models.Model):
    """Tweet. Se repost_of estiver preenchido, é um repost (content vazio)."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=280, blank=True)
    repost_of = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="reposts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "post")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
