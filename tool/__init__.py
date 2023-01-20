from __future__ import annotations

import os.path
from pathlib import Path

from config import settings


def validate(path: Path):
    if not os.path.exists(path) and settings.debug:
        raise FileNotFoundError(path)
    elif os.path.exists(path):
        return path
    else:
        raise Exception("ValidationError")


base_dir = Path(__file__).resolve().parent

geth_dir = validate(base_dir / "geth")
geth_exe = validate(geth_dir / "geth.exe")
clef_exe = validate(geth_dir / "clef.exe")
clef_rules = validate(base_dir / "celf_rules.js")

influx_db_dir = validate(base_dir / "influxdb")
influx_db_exe = validate(influx_db_dir / "influxd.exe")
influx_cli_exe = validate(influx_db_dir / "influx.exe")

grafana_dir = validate(base_dir / "grafana")
grafana_cli_exe = validate(grafana_dir / "grafana-cli.exe")
grafana_server_exe = validate(grafana_dir / "grafana-server.exe")
