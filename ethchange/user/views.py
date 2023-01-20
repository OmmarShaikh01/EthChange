from __future__ import annotations

from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from ethchange.user.models import UserModel, UserModelSerializer


@api_view(["POST"])
@parser_classes([JSONParser])
@permission_classes([AllowAny])
def signup(request: Request) -> Response:
    user_info = dict()
    req_data = request.data

    if "password" in req_data.keys():
        user_info["password"] = req_data["password"]
    else:
        return Response(dict(message="Missing UserInfoAttribute [password]"), status=status.HTTP_400_BAD_REQUEST)

    if "name" in req_data.keys():
        user_info["name"] = req_data["name"]
        if UserModel.objects.filter(name=req_data["name"]).first():
            return Response(dict(message="User Account Exists"), status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(dict(message="Missing UserInfoAttribute [name]"), status=status.HTTP_400_BAD_REQUEST)

    if "phone" in req_data.keys() and (
            isinstance(req_data.get("phone"), int) and 1000000000 <= req_data.get("phone") <= 9999999999
    ):
        user_info["phone"] = req_data["phone"]
    else:
        return Response(dict(message="Missing UserInfoAttribute [phone]"), status=status.HTTP_400_BAD_REQUEST)

    if "email" in req_data.keys():
        user_info["email"] = req_data["email"]
    else:
        return Response(dict(message="Missing UserInfoAttribute [email]"), status=status.HTTP_400_BAD_REQUEST)

    if UserModel.objects.create_user(**user_info) is not None:
        user = authenticate(request, name=user_info["name"], password=user_info["password"])
        if user is not None:
            _login(request, user)
            user.save()
            return Response({"message": "Success"}, status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@parser_classes([JSONParser])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    user_info = dict()
    req_data = request.data

    if "password" in req_data.keys():
        user_info["password"] = req_data["password"]
    else:
        return Response(dict(message="Missing UserInfoAttribute [password]"), status=status.HTTP_400_BAD_REQUEST)

    if "name" in req_data.keys():
        user = UserModel.objects.filter(name=req_data["name"]).first()

    elif "phone" in req_data.keys():
        user = UserModel.objects.filter(phone=req_data["phone"]).first()

    elif "email" in req_data.keys():
        user = UserModel.objects.filter(email=req_data["email"]).first()

    else:
        return Response(dict(message="Missing UserInfoAttributes"), status=status.HTTP_400_BAD_REQUEST)

    if user:
        password = req_data["password"]
        user = authenticate(request, username=user.name, password=password)
        if user is not None:
            _login(request, user)
            user.save()

        return Response({"message": "Success"}, status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserModelSerializer
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]

    def list(self, request: Request, *args, **kwargs) -> Response:
        user = UserModel.objects.all()
        if user:
            serializer = self.get_serializer_class()(user, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: Request, pk: Optional[str] = None, *args, **kwargs) -> Response:
        user = UserModel.objects.filter(name=pk).first()
        if user:
            serializer = self.get_serializer_class()(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(basename="user", name="logout", methods=["POST"], detail=True)
    def logout(self, request: Request, pk: Optional[str] = None) -> Response:
        user = UserModel.objects.filter(name=pk).first()
        if user:
            _logout(request)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(basename="user", name="lock_wallet", methods=["POST"], detail=True)
    def lock_wallet(self, request: Request, pk: Optional[str] = None) -> Response:
        if "password" not in request.data.keys():
            return Response(dict(message="Missing UserInfoAttribute [password]"), status=status.HTTP_400_BAD_REQUEST)

        data = UserModel.objects.lock_wallet(name=pk, password=request.data["password"])
        if data:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(basename="user", name="unlock_wallet", methods=["POST"], detail=True)
    def unlock_wallet(self, request: Request, pk: Optional[str] = None) -> Response:
        if "password" not in request.data.keys():
            return Response(dict(message="Missing UserInfoAttribute [password]"), status=status.HTTP_400_BAD_REQUEST)

        data = UserModel.objects.unlock_wallet(name=pk, password=request.data["password"])
        if data:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(basename="user", name="balance_eth_account", methods=["GET"], detail=True)
    def balance_eth_account(self, request: Request, pk: Optional[str] = None) -> Response:
        from loguru import logger

        logger.info(request.data)
        if "password" not in request.data.keys():
            return Response(dict(message="Missing UserInfoAttribute [password]"), status=status.HTTP_400_BAD_REQUEST)

        data = UserModel.objects.balance_eth_account(name=pk, password=request.data["password"])
        if data is not None:
            return Response(data=dict(balance=data), status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
