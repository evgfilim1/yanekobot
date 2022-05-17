__all__ = [
    "AccountsType",
    "BotConfig",
    "CategoryConfig",
    "Config",
    "parse_config",
    "ParserConfig",
    "RedisConfig",
    "SourceConfig",
    "StorageConfig",
]

from pathlib import Path
from typing import Any, TypeAlias, cast

import yaml
from pydantic import AnyHttpUrl, BaseModel, FileUrl, RedisDsn, root_validator, validator

AccountsType: TypeAlias = dict[str, dict[str, Any] | None]


class BotConfig(BaseModel):
    """Telegram bot configuration."""

    token: str
    """Telegram bot token."""
    api_url: AnyHttpUrl | None = None
    """(Optional) Telegram local API URL, defaults to `"https://api.telegram.org"`."""
    admin_id: list[int]
    """Admin chat IDs, everything is allowed from admin chats."""
    allow_edit: bool
    """Allow editing picture category."""
    allow_delete: bool
    """Allow moving pictures to "trash"."""
    delete_after_send: bool
    """Delete picture from disk after it's sent to Telegram."""
    delete_from_disk: bool
    """Delete picture from disk after moving to trash (implies `delete_from_db=True`)."""
    delete_from_db: bool
    """Delete picture from database after moving to trash."""


class RedisConfig(BaseModel):
    """Redis database configuration."""

    host: str
    """Redis host."""
    port: int
    """Redis port."""
    password: str | None = None
    """(Optional) Redis password, defaults to `""`."""
    db: int = 0
    """(Optional) Redis database, defaults to `0`."""
    key_prefix: str
    """Key prefix for bot data."""

    @validator("port")
    def check_port(cls, v: int) -> int:
        """Check that port is in range 1-65535."""
        if not 0 < v < 65536:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator("db")
    def check_db(cls, v: int) -> int:
        """Check that db is non-negative."""
        if v < 0:
            raise ValueError("Database must be a non-negative integer")
        return v

    @property
    def url(self) -> str:
        """Redis connection URL."""
        return cast(
            str,
            RedisDsn.build(
                scheme="redis://",
                host=self.host,
                port=str(self.port),
                password=self.password,
                db=str(self.db),
            ),
        )


class ParserConfig(BaseModel):
    """Userbot parser configuration."""

    app_id: int
    """Telegram User API app_id."""
    app_hash: str
    """Telegram User API app_hash."""
    accounts: AccountsType
    """Account configuration dictionary.
    Key is account name.
    Value is (optional) kwargs which will be passed to `pyrogram.Client` directly, defaults to `{}`.
    """

    @validator("accounts")
    def check_accounts(cls, v: AccountsType) -> AccountsType:
        """Check that accounts are non-empty."""
        if len(v) == 0:
            raise ValueError("At least one account must be specified")
        return v


class StorageConfig(BaseModel):
    """Storage configuration."""

    url: AnyHttpUrl | FileUrl
    """URL where to get pictures, will be used as base for sending pictures.
    If using local bot api server, file:/// protocol can be specified.
    """
    base_path: Path
    """Path where to save all data like pictures, trash, account sessions, etc."""

    @validator("base_path")
    def check_base_path(cls, v: Path) -> Path:
        """Check that base path is an existing directory, creating it if not exists."""
        v = v.resolve()
        if not v.exists():
            v.mkdir(parents=True)
        if not v.is_dir():
            raise ValueError("Base path must be a directory")
        return v


class SourceConfig(BaseModel):
    """Category source configuration."""

    id: int | str
    """ID or username of the channel."""
    user: str | None = None
    """(Optional) User which will be used to parse the channel. Must be present in `accounts`.
    Mandatory for private channels. Defaults to a random account from `accounts`.
    """

    @root_validator()
    def check_config(cls, values: dict[str, int | str]) -> dict[str, int | str]:
        """Checks that user is specified with private channel."""
        if isinstance(values["id"], str):
            try:
                # Trying to cast this to `int`
                values["id"] = int(values["id"])
            except ValueError:
                # `id` is a username, everything is fine
                return values
        if values["user"] is None:
            raise ValueError("`user` must be specified for numeric `id`s")
        return values


class CategoryConfig(BaseModel):
    """Category configuration."""

    sources: list[SourceConfig] = []
    """(Optional) Picture sources, defaults to `[]`."""
    aliases: list[str] = []
    """(Optional) Text aliases, an alternative way to trigger sending a picture, defaults to `[]`.
    Aliases are case-insensitive. They will work only when the bot is an admin in the chat.
    """
    captions: list[str] = []
    """(Optional) Captions for pictures, will be chosen randomly, defaults to `[]`."""
    hidden: bool = False
    """(Optional) Is this category hidden in Telegram command menu? Defaults to `False`."""
    nsfw: bool = False
    """(Optional) Mark this category as not safe for work (nudity, erotic content, etc.). 
    Defaults to `False`.
    """


class Config(BaseModel):
    """Application configuration object."""

    bot: BotConfig
    """Telegram bot configuration."""
    redis: RedisConfig
    """Redis database configuration."""
    parser: ParserConfig
    """Userbot parser configuration."""
    storage: StorageConfig
    """Storage configuration."""
    categories: dict[str, CategoryConfig]
    """Category configuration."""


def parse_config(path: Path) -> Config:
    """Parses config file."""
    with path.open() as f:
        return Config.parse_obj(yaml.safe_load(f))
