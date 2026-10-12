from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Comment, Post

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "name", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name", read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "name", "avatar", "followers_count", "following_count", "is_following"]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated
                    and request.user.following.filter(pk=obj.pk).exists())


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Todos os campos são opcionais: o usuário altera só o que quiser."""
    name = serializers.CharField(source="first_name", required=False, max_length=150)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["name", "avatar", "password", "current_password"]

    def validate(self, attrs):
        new_pw = attrs.get("password")
        if new_pw:
            current = attrs.get("current_password")
            if not current or not self.instance.check_password(current):
                raise serializers.ValidationError({"current_password": "Senha atual incorreta."})
            validate_password(new_pw, self.instance)
        return attrs

    def update(self, instance, validated_data):
        new_pw = validated_data.pop("password", None)
        validated_data.pop("current_password", None)
        instance = super().update(instance, validated_data)
        if new_pw:
            instance.set_password(new_pw)
            instance.save()
        return instance


class PostBaseSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    reposts_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "content", "likes_count", "comments_count",
                  "reposts_count", "liked_by_me", "created_at"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reposts_count(self, obj):
        return obj.reposts.count()

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated
                    and obj.likes.filter(user=request.user).exists())


class PostSerializer(PostBaseSerializer):
    content = serializers.CharField(max_length=280)  # obrigatório ao criar/editar
    repost_of = PostBaseSerializer(read_only=True)

    class Meta(PostBaseSerializer.Meta):
        fields = PostBaseSerializer.Meta.fields + ["repost_of"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
