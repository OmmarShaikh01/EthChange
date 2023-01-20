from __future__ import annotations

from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ethchange.user"

    def ready(self):
        from ethchange import injector

        injector.wire(modules=["ethchange.user.models"])
