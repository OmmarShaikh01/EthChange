import os
from pathlib import PurePath

BASE_DIR = PurePath(os.path.dirname(__file__))


def execute_cmd(cmd: list):
    return os.system(" ".join(list(map(str, cmd))))


def run_server():
    execute_cmd(
        [
            BASE_DIR / ".venv" / "Scripts" / "python.exe",
            "-m",
            "manage",
            "runserver"
        ]
    )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "task",
        choices=[
            "runserver"
        ]
    )

    original_dir = os.getcwd()
    os.chdir(BASE_DIR)

    args = parser.parse_args()
    match args.task:
        case "runserver":
            run_server()

    os.chdir(original_dir)
