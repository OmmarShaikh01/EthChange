from __future__ import annotations

import uuid
from typing import Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as ModelUserManager
from django.db import models
from loguru import logger


# noinspection PyMethodOverriding
class UserManager(ModelUserManager):
    """UserManager"""

    def _create_user(self, name: str, password: str, phone: int, email: str, **extra_fields) -> UserModel:
        if not name:
            raise ValueError("The given username must be set")

        email = self.normalize_email(email)
        name = self.model.normalize_username(name)
        password = make_password(password)
        user = self.model(name=name, password=password, phone=phone, email=email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, name: str, password: str, phone: int, email: str, **extra_fields) -> UserModel:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self._create_user(name, password, phone, email, **extra_fields)
        logger.opt(lazy=True).debug(f"[{user}] Created as Normal User")
        return user

    def create_superuser(self, name: str, password: str, phone: int, email: str, **extra_fields) -> UserModel:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self._create_user(name, password, phone, email, **extra_fields)
        logger.opt(lazy=True).debug(f"[{user}] Created as Super User")
        return user

    def change_password(self, new_password: str, email: str, phone: str) -> Optional[UserModel]:
        user: Optional[UserModel] = self.filter(email=email, phone=phone).first()
        if user:
            password = make_password(new_password)
            user.password = password
            user.save(using=self._db)
            logger.opt(lazy=True).debug(f"[{user}] Password Change Request Successful")
            return user
        logger.opt(lazy=True).debug(f"[{user}] Password Change Request Failed")

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        return super().with_perm(perm, is_active, include_superusers, backend, obj)


class UserModel(AbstractBaseUser, PermissionsMixin):
    """UserModel"""

    objects = UserManager()

    pkid = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, blank=False)
    name = models.CharField(unique=True, blank=False, max_length=128)
    email = models.EmailField(unique=True, blank=False, max_length=128)
    phone = models.IntegerField(unique=True, blank=False)
    password = models.CharField(unique=True, blank=False, max_length=128)

    is_staff = models.BooleanField(default=False, blank=False)
    is_superuser = models.BooleanField(default=False, blank=False)

    USERNAME_FIELD = "name"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "phone", "password"]
