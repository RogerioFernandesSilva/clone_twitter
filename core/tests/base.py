import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from core.models import Post

User = get_user_model()
PASSWORD = "Senha@12345"


def image_file(name="a.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class BaseTest(APITestCase):
    password = PASSWORD

    def make_user(self, username, **kw):
        return User.objects.create_user(username=username, password=PASSWORD, **kw)

    def login(self, user):
        self.client.force_authenticate(user)

    def make_post(self, author, content="Olá mundo"):
        return Post.objects.create(author=author, content=content)
