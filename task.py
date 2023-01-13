"""
Task Runner
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import time
from concurrent.futures import Executor, ProcessPoolExecutor
from pathlib import PurePath
from typing import Optional

BASE_DIR = PurePath(os.path.dirname(__file__))


def execute_cmd(cmd: list, quite: bool = False):
    if not quite:
        print(f"Executing [{shlex.join(list(map(str, cmd)))}]")

    exe = subprocess.call(list(map(str, cmd)))

    if not quite:
        print("Completed ...\n")

    return exe


def execute_cmd_background(executor: Executor, cmd: list, quite: bool = False):
    if not quite:
        print(f"Executing [{shlex.join(list(map(str, cmd)))}]")

    executor.submit(subprocess.call, cmd)

    if not quite:
        print("Completed ...\n")


def run_server(executor: Executor, parser: Optional[argparse.Namespace] = None):
    if parser is not None and parser.reformat:
        run_reformatter()

    common_commands = [BASE_DIR / ".venv" / "Scripts" / "python.exe", "-m", "manage"]
    execute_cmd([*common_commands, "makemigrations", "--noinput", "--no-header"])
    execute_cmd([*common_commands, "migrate", "--run-syncdb", "--noinput"])

    if parser is not None and parser.flush:
        flush_server()

    execute_cmd_background(executor, [*common_commands, "runserver"])


def flush_server(parser: Optional[argparse.Namespace] = None):
    common_commands = [BASE_DIR / ".venv" / "Scripts" / "python.exe", "-m", "manage"]
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
    execute_cmd([BASE_DIR / ".venv" / "Scripts" / "isort.exe", "."])
    execute_cmd([BASE_DIR / ".venv" / "Scripts" / "black.exe", "."])


def run_services(executor: Executor):
    from tool import foundry_anvil, foundry_anvil_json

    execute_cmd_background(
        executor,
        [
            foundry_anvil,
            "--accounts",
            "10",
            "--balance",
            "100",
            "--no-mining",
            "--no-cors",
            "--config-out",
            foundry_anvil_json,
        ],
    )


def main():
    t1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["runserver", "reformat"])
    parser.add_argument("--run-services", action="store_true")

    parser_runserver = parser.add_argument_group("runserver")
    parser_runserver.add_argument("--reformat", action="store_true")
    parser_runserver.add_argument("--flush", action="store_true")

    original_dir = os.getcwd()
    os.chdir(BASE_DIR)
    os.system("cls")

    args = parser.parse_args()
    try:
        with ProcessPoolExecutor() as pool_exe:
            if args.run_services:
                run_services(pool_exe)

            match args.task:
                case "runserver":
                    run_server(pool_exe, args)
                case "reformat":
                    run_reformatter()

    except KeyboardInterrupt:
        print(f"Executed [{args.task}] in {round(time.time() - t1, 4)} Sec")

    os.chdir(original_dir)


if __name__ == "__main__":
    main()
