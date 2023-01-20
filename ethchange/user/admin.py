from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from ethchange.user.models import UserModel


class UserModelChangeForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ("name", "email", "phone", "password")


class UserModelCreationForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ("name", "email", "phone", "password")


@admin.register(UserModel)
class UserModelAdmin(BaseUserAdmin):
    """
    Admin class for Usermodel
    """

    form = UserModelChangeForm
    add_form = UserModelCreationForm
    exclude = (
        "last_name",
        "is_active",
        "username",
        "first_name",
        "date_joined",
        "is_staff",
    )

    fieldsets = (
        (
            "Account Information",
            {
                "classes": ("wide",),
                "fields": ("name", "email", "phone", "password"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "email", "phone", "password"),
            },
        ),
    )

    list_display = (
        "name",
        "phone",
        "email",
        "is_superuser",
        "is_staff",
        "eth_account",
    )

    list_filter = (
        "name",
        "phone",
        "email",
        "is_superuser",
        "is_staff",
    )
    ordering = ["name"]
    filter_horizontal = []


admin.site.unregister(Group)
