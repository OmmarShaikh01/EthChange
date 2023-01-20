from __future__ import annotations

from loguru import logger

from ethchange.providers import ProviderContainer

injector = ProviderContainer()
logger.success("Injector Intilized")
