"""
ethchange URL Configuration
"""
from __future__ import annotations

from django.contrib import admin
from django.urls import path

from ethchange.user.urls import urlpatterns as user_urlpatterns

urlpatterns = [path("admin/", admin.site.urls), *user_urlpatterns]
