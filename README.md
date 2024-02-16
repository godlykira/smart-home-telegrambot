# smart-home

[![CodeQL](https://github.com/godlykira/smart-home-telegrambot/workflows/CodeQL/badge.svg)](https://github.com/godlykira/smart-home-telegrambot/actions?query=workflow%3ACodeQL)

## About

### Telegram Bot for Raspberry Pi Control

This Python project showcases a Telegram bot designed to control Raspberry Pi hardware. The bot allows users to interact with the Raspberry Pi, sending commands such as turning on/off lights using GPIO pins. The project integrates the `python-telegram-bot` library for Telegram interaction and `RPi.GPIO` for GPIO control. Environment variables, including the Telegram bot token, are managed using `python-dotenv` for secure configuration. This serves as a foundation for creating custom Raspberry Pi-controlled applications through Telegram.

## Installation

To install all the requirement packages, run this command;

```bash
pip install -r requirements.txt
```
or

```bash
pip install python-telegram-bot
pip install "python-telegram-bot[job-queue]"
```

After installation, create `.env` file and write
```txt
BOT_TOKEN=<bot-token>
```
Finally, run `main.py` using the following command;
```bash
python main.py
```

## Supported OS
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Windows 11](https://img.shields.io/badge/Windows%2011-%230079d5.svg?style=for-the-badge&logo=Windows%2011&logoColor=white)
