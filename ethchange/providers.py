from __future__ import annotations

from dependency_injector import containers
from dependency_injector.providers import Factory
from web3 import Web3

from config import settings


class ProviderContainer(containers.DeclarativeContainer):
    web3_provider = Factory(Web3, Web3.HTTPProvider(settings.node_uri))
