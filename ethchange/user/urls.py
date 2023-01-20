from __future__ import annotations

from django.urls import path
from rest_framework import routers

from ethchange.user.views import UserViewSet, login, signup

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)
urlpatterns = (path("users/login/", login, name="login"), path("users/signup/", signup, name="signup"), *router.urls)
