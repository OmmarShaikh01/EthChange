"""
Task Runner
"""
from __future__ import annotations

import argparse
import datetime
import os
import shlex
import subprocess
import time
from concurrent.futures import Executor, ProcessPoolExecutor
from pathlib import PurePath
from typing import Optional

BASE_DIR = PurePath(os.path.dirname(__file__))


def set_up_tasks():
    required_file = (
        (BASE_DIR / "volume"),
        (BASE_DIR / "volume" / "geth"),
        (BASE_DIR / "volume" / "geth" / "keystore"),
        (BASE_DIR / "volume" / "geth" / "clef"),
        (BASE_DIR / "volume" / "geth" / "clef.ipc"),
        (BASE_DIR / "volume" / "geth" / "ethereum"),
        (BASE_DIR / "volume" / "geth" / "ethash"),
        (BASE_DIR / "volume" / "logs"),
    )

    for path in filter(lambda x: not os.path.exists(x), required_file):
        if os.path.splitext(path)[1]:
            open(path, "w", encoding="utf-8").close()
        elif not os.path.splitext(path)[1]:
            os.mkdir(path)


def execute_cmd(cmd: list, quite: bool = False):
    if not quite:
        print(f"Executing [{shlex.join(list(map(str, cmd)))}]")

    exe = subprocess.call(list(map(str, cmd)))

    if not quite:
        print("Completed ...\n")

    return exe


def execute_cmd_background(executor: Executor, cmd: list, quite: bool = False, **kwargs):
    cmd = ["start", "/W", *cmd]
    if not quite:
        print(f"Starting [{shlex.join(list(map(str, cmd)))}]")
    executor.submit(subprocess.check_output, shlex.join(list(map(str, cmd))), shell=True, **kwargs)
    time.sleep(2)
    if not quite:
        print("Completed ...\n")


def run_server(executor: Executor, parser: Optional[argparse.Namespace] = None):
    if parser is not None and parser.reformat:
        run_reformatter()

    common_commands = [(BASE_DIR / ".venv" / "Scripts" / "python.exe").as_posix(), "-m", "manage"]
    execute_cmd([*common_commands, "makemigrations", "--noinput", "--no-header"])
    execute_cmd([*common_commands, "migrate", "--run-syncdb", "--noinput"])

    if parser is not None and parser.flush:
        flush_server()

    execute_cmd_background(executor, [*common_commands, "runserver"])


def flush_server(parser: Optional[argparse.Namespace] = None):
    common_commands = [(BASE_DIR / ".venv" / "Scripts" / "python.exe").as_posix(), "-m", "manage"]
    execute_cmd([*common_commands, "flush", "--noinput"])
    execute_cmd(
        [
            *common_commands,
            "createsuperuser",
            "--noinput",
            "--name",
            "admin_user",
            "--email",
            "admin_user@testmail.com",
            "--phone",
            "3214569870",
            "--password",
            "qwerty123456",
        ]
    )


def run_reformatter(parser: Optional[argparse.Namespace] = None):
    execute_cmd([(BASE_DIR / ".venv" / "Scripts" / "isort.exe").as_posix(), "."])
    execute_cmd([(BASE_DIR / ".venv" / "Scripts" / "black.exe").as_posix(), "."])


def service_geth(executor: Executor):
    from config import settings
    from tool import geth_exe

    # geth
    execute_cmd_background(
        executor,
        [
            geth_exe.as_posix(),
            *("--goerli", "--pprof"),
            *("--keystore", (BASE_DIR / "volume" / "geth" / "keystore").as_posix()),
            *("--identity", "ethchange"),
            *("--datadir", (BASE_DIR / "volume" / "geth" / "ethereum").as_posix()),
            *("--ethash.dagdir", (BASE_DIR / "volume" / "geth" / "ethash").as_posix()),
            *("--http", "--http.addr", settings.node_addr, "--http.port", settings.node_port),
            *("--http.api", "eth,net,web3,personal"),
        ],
    )


def main():
    t1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["runservices", "runserver", "reformat"])
    parser.add_argument("--run-services", action="store_true")

    parser_runserver = parser.add_argument_group("runserver")
    parser_runserver.add_argument("--reformat", action="store_true")
    parser_runserver.add_argument("--flush", action="store_true")

    original_dir = os.getcwd()
    os.chdir(BASE_DIR)

    args = parser.parse_args()
    # noinspection PyBroadException
    try:
        set_up_tasks()

        with ProcessPoolExecutor() as pool_exe:
            if args.run_services and not args.task == "runservices":
                service_geth(pool_exe)

            match args.task:
                case "runserver":
                    run_server(pool_exe, args)
                case "reformat":
                    run_reformatter()
                case "runservices":
                    service_geth(pool_exe)

    except KeyboardInterrupt:
        exe_time = datetime.timedelta(seconds=round(time.time() - t1, 4))
        print(f"Executed [{args.task}] in {exe_time}")

    except Exception as e:
        os.chdir(original_dir)
        raise e


if __name__ == "__main__":
    main()
