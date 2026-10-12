from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Like, Post, User

admin.site.register(User, UserAdmin)
admin.site.register([Post, Like, Comment])
