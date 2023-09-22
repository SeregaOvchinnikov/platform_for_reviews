from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, signup, token)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"
v1_router = DefaultRouter()
v1_router.register("genres", GenreViewSet, basename="genres")
v1_router.register("categories", CategoryViewSet, basename="categories")
v1_router.register("titles", TitleViewSet, basename="titles")
v1_router.register("users", UserViewSet, basename="users")
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet,
    basename="title-reviews"
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="review-comments",
)

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/signup/", signup, name="signup"),
    path("v1/auth/token/", token, name="login"),
]
