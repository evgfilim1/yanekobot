__all__ = ["main"]

import logging
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from . import __version__
from .config import Config, parse_config


@dataclass()
class CLIArgs:
    config: Path
    log_level: str
    action: str


@dataclass()
class RunCLIArgs(CLIArgs):
    def __post_init__(self) -> None:
        if self.action != "run":
            raise ValueError(f"Invalid action for {type(self).__name__}: {self.action}")


@dataclass()
class WebhookCLIArgs(CLIArgs):
    host: str
    port: int
    path: str
    url: str

    def __post_init__(self) -> None:
        if self.action != "webhook":
            raise ValueError(f"Invalid action for {type(self).__name__}: {self.action}")


@dataclass()
class ParseCLIArgs(CLIArgs):
    category: list[str]
    interactive: bool
    dry_run: bool

    def __post_init__(self) -> None:
        if self.action != "parse":
            raise ValueError(f"Invalid action for {type(self).__name__}: {self.action}")


def _existing_file(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise ValueError(f"{path} does not exist")
    if not path.is_file():
        raise ValueError(f"{path} is not a file")
    return path


def parse_args(args: Sequence[str]) -> CLIArgs:
    parser = ArgumentParser(
        description="Yet Another Nekobot for Telegram",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=_existing_file,
        help="config file",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--log-level",
        help="log level",
        choices=["debug", "info", "warning", "error"],
        default="info",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"YANekoBot v{__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="action",
        help="action to perform",
        required=False,
    )

    subparsers.add_parser("run", help="run bot with polling (default)")

    webhook = subparsers.add_parser("webhook", help="run bot with webhook")
    webhook.add_argument(
        "--host",
        help="host to listen on, defaults to localhost",
        default="localhost",
    )
    webhook.add_argument(
        "-p",
        "--port",
        type=int,
        help="port to listen on, defaults to 8443",
        default=8443,
    )
    webhook.add_argument(
        "--path",
        help="path to listen on, defaults to /",
        default="/",
    )
    webhook.add_argument(
        "url",
        help="url to set webhook to",
    )

    parse = subparsers.add_parser("parse", help="parse chats")
    parse.add_argument(
        "category",
        nargs="*",
        help="category to parse, defaults to all",
    )
    parse.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="interactive mode",
    )
    parse.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="dry run",
    )

    ns = parser.parse_args(args)
    match ns.action:
        case "run" | "" | None:
            ns.action = "run"
            return RunCLIArgs(**ns.__dict__)
        case "webhook":
            return WebhookCLIArgs(**ns.__dict__)
        case "parse":
            return ParseCLIArgs(**ns.__dict__)
    raise AssertionError("Invalid action, this should not happen")


def _main_run(_: RunCLIArgs, config: Config) -> None:
    from .bot_runner import run_polling

    run_polling(config)


def _main_webhook(args: WebhookCLIArgs, config: Config) -> None:
    from .bot_runner import run_webhook

    run_webhook(config, args.host, args.port, args.path, args.url)


def _main_parse(args: ParseCLIArgs, config: Config) -> None:
    # from .parser import run_parser

    ...


def main() -> None:
    args = parse_args(sys.argv[1:])
    logging.basicConfig(
        level=args.log_level.upper(),
        format="[{levelname:<7}] {message}",
        style="{",
    )
    config = parse_config(args.config)
    match args:
        case RunCLIArgs() as a:
            return _main_run(a, config)
        case WebhookCLIArgs() as a:
            return _main_webhook(a, config)
        case ParseCLIArgs() as a:
            return _main_parse(a, config)
    raise AssertionError("Invalid action, this should not happen")
