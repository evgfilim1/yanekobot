# YANekoBot

[![wakatime](https://wakatime.com/badge/github/evgfilim1/yanekobot.svg)](https://wakatime.com/badge/github/evgfilim1/yanekobot)
[![black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[WIP] Yet Another Nekobot for Telegram, rewritten to be open source.

## Features
- Can send random pictures
- Can send a cat kaomoji on "nya"

## Installation
- Clone the repository: `git clone https://github.com/evgfilim1/yanekobot`
- Setup a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install dependencies: `pip install -e .[parser]`
  - Add `dev` extra for development: `pip install -e .[parser,dev]`
- Copy `config.sample.yaml` to `config.yaml` and edit the latter
- Run the parser: `python -m nekobot -c config.yaml parse` (not yet implemented)
- Run the bot: `python -m nekobot -c config.yaml`
