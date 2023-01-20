from __future__ import annotations

import uuid
from typing import Optional

from dependency_injector.wiring import Provide, inject
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as ModelUserManager
from django.db import models
from loguru import logger
from rest_framework import serializers
from web3 import Web3

from ethchange import ProviderContainer


# noinspection PyMethodOverriding
class UserManager(ModelUserManager):
    """UserManager"""

    @inject
    def _generate_eth_account(self, password: str, web3: Web3 = Provide[ProviderContainer.web3_provider]) -> bytes:
        account = web3.geth.personal.new_account(password).encode("utf-8")
        if account:
            return account
        else:
            return b""

    @inject
    def lock_eth_account(self, name: str, password: str, web3: Web3 = Provide[ProviderContainer.web3_provider]) -> bool:
        user = self.filter(name=name, password=make_password(password)).first()
        if user:
            web3.geth.personal.lock_account(user.eth_account)
        return bool(user)

    @inject
    def unlock_eth_account(
            self, name: str, password: str, web3: Web3 = Provide[ProviderContainer.web3_provider]
    ) -> bool:
        user = self.filter(name=name, password=make_password(password)).first()
        if user:
            web3.geth.personal.unlock_account(user.eth_account, passphrase=password)
        return bool(user)

    @inject
    def balance_eth_account(
            self, name: str, password: str, web3: Web3 = Provide[ProviderContainer.web3_provider]
    ) -> Optional[int]:
        user = self.filter(name=name).first()
        if user:
            return web3.eth.get_balance(account=user.eth_account.decode("utf-8"))

    def _create_user(self, name: str, password: str, phone: int, email: str, **extra_fields) -> Optional[UserModel]:
        if not name:
            raise ValueError("The given username must be set")

        if not self.filter(name=name).first():
            email = self.normalize_email(email)
            name = self.model.normalize_username(name)
            eth_account = self._generate_eth_account(password=password)
            password = make_password(password)
            if eth_account:
                user = self.model(
                    name=name, password=password, phone=phone, email=email, eth_account=eth_account, **extra_fields
                )
                user.save(using=self._db)
                return user

    def remove_user(self, name: str) -> bool:
        # password = make_password(password)
        deleted = self.filter(name=name).delete()
        logger.opt(lazy=True).debug(f"[{deleted}] Deleted User")
        return bool(deleted[0])

    def create_user(self, name: str, password: str, phone: int, email: str, **extra_fields) -> Optional[UserModel]:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self._create_user(name, password, phone, email, **extra_fields)
        if user:
            logger.opt(lazy=True).debug(f"[{user}] Created as Normal User")
            return user

    def create_superuser(self, name: str, password: str, phone: int, email: str, **extra_fields) -> Optional[UserModel]:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self._create_user(name, password, phone, email, **extra_fields)
        if user:
            logger.opt(lazy=True).debug(f"[{user}] Created as Super User")
            return user

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        return super().with_perm(perm, is_active, include_superusers, backend, obj)


class UserModel(AbstractBaseUser, PermissionsMixin):
    """UserModel"""

    objects = UserManager()

    pkid = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, blank=False)
    eth_account = models.BinaryField(unique=True, blank=False, max_length=20)
    name = models.CharField(unique=True, blank=False, max_length=128)
    email = models.EmailField(unique=True, blank=False, max_length=128)
    phone = models.IntegerField(unique=True, blank=False)
    password = models.CharField(unique=True, blank=False, max_length=128)

    is_staff = models.BooleanField(default=False, blank=False)
    is_superuser = models.BooleanField(default=False, blank=False)

    USERNAME_FIELD = "name"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "phone", "password"]


class UserModelSerializer(serializers.ModelSerializer):
    """
    User Model Serializer
    """

    class Meta:
        model = UserModel
        fields = [
            "eth_account",
            "name",
            "email",
            "phone",
        ]
