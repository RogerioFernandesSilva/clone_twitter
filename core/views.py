from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Like, Post
from .serializers import (CommentSerializer, PostSerializer, ProfileUpdateSerializer,
                          RegisterSerializer, UserSerializer)

User = get_user_model()


# ---------- Autenticação e perfil ----------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        s = ProfileUpdateSerializer(request.user, data=request.data, partial=True,
                                    context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)

    put = patch


# ---------- Usuários e seguidores ----------
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.exclude(pk=self.request.user.pk).order_by("username")
        q = self.request.query_params.get("search")
        return qs.filter(username__icontains=q) if q else qs


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"


@api_view(["POST", "DELETE"])
def follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return Response({"detail": "Você não pode seguir a si mesmo."}, status=400)
    if request.method == "POST":
        request.user.following.add(target)
    else:
        request.user.following.remove(target)
    return Response(UserSerializer(target, context={"request": request}).data)


class FollowersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return get_object_or_404(User, username=self.kwargs["username"]).followers.order_by("username")


class FollowingView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return get_object_or_404(User, username=self.kwargs["username"]).following.order_by("username")


# ---------- Feed ----------
class FeedView(generics.ListAPIView):
    """Somente postagens (e reposts) de quem o usuário segue."""
    serializer_class = PostSerializer

    def get_queryset(self):
        return (Post.objects.filter(author__in=self.request.user.following.all())
                .select_related("author", "repost_of__author"))


# ---------- Postagens ----------
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action in ("update", "partial_update", "destroy"):
            return obj.author == request.user
        return True


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related("author", "repost_of__author")
        author = self.request.query_params.get("author")
        return qs.filter(author__username=author) if author else qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.repost_of_id:
            raise ValidationError({"detail": "Reposts não podem ser editados."})
        serializer.save()

    def _ser(self, post, **kw):
        return PostSerializer(post, context={"request": self.request}).data

    @action(detail=True, methods=["post"])
    def repost(self, request, pk=None):
        original = self.get_object()
        if original.repost_of_id:  # repost de repost aponta para o original
            original = original.repost_of
        if Post.objects.filter(author=request.user, repost_of=original).exists():
            return Response({"detail": "Você já repostou esta postagem."}, status=400)
        post = Post.objects.create(author=request.user, repost_of=original)
        return Response(self._ser(post), status=201)

    @action(detail=True, methods=["post", "delete"])
    def like(self, request, pk=None):
        post = self.get_object()
        code = 200
        if request.method == "POST":
            _, created = Like.objects.get_or_create(user=request.user, post=post)
            code = 201 if created else 200
        else:
            Like.objects.filter(user=request.user, post=post).delete()
        return Response(self._ser(post), status=code)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            page = self.paginate_queryset(post.comments.select_related("user"))
            data = CommentSerializer(page, many=True, context={"request": request}).data
            return self.get_paginated_response(data)
        s = CommentSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save(user=request.user, post=post)
        return Response(s.data, status=201)


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Apenas o autor pode apagar o comentário.")
        instance.delete()
