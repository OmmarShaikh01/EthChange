import os
from pathlib import PurePath

from dynaconf import Dynaconf

validators = ()

settings = Dynaconf(
    env_switcher="APP_MODE",
    envvar_prefix="DYNACONF",
    default_env="DEVELOPMENT",
    env="DEVELOPMENT",
    root_path=PurePath(os.path.dirname(__file__)) / "config",
    environments=["DEFAULT", "DEVELOPMENT", "PRODUCTION"],
    settings_files=["settings.toml", ".secrets.toml"],
    validators=validators,
)
