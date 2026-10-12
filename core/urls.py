from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = SimpleRouter()
router.register("posts", views.PostViewSet, basename="post")

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("api/auth/register/", views.RegisterView.as_view()),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/profile/", views.MeView.as_view()),
    path("api/users/", views.UserListView.as_view()),
    path("api/users/<str:username>/", views.UserDetailView.as_view()),
    path("api/users/<str:username>/follow/", views.follow),
    path("api/users/<str:username>/followers/", views.FollowersView.as_view()),
    path("api/users/<str:username>/following/", views.FollowingView.as_view()),
    path("api/feed/", views.FeedView.as_view()),
    path("api/comments/<int:pk>/", views.CommentDeleteView.as_view()),
]
urlpatterns += [path("api/", include(router.urls))]
