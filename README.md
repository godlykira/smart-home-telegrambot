# smart-home

## About

### Telegram Bot for Raspberry Pi Control

This Python project showcases a Telegram bot designed to control Raspberry Pi hardware. The bot allows users to interact with the Raspberry Pi, sending commands such as turning on/off lights using GPIO pins. The project integrates the `python-telegram-bot` library for Telegram interaction and `RPi.GPIO` for GPIO control. Environment variables, including the Telegram bot token, are managed using `python-dotenv` for secure configuration. This serves as a foundation for creating custom Raspberry Pi-controlled applications through Telegram.

## Installation

To install all the requirement packages, run this command;

```powershell
pip install -r requirements.txt
```
After installation, create `.env` file and write
```
BOT_TOKEN= <bot-token>
```
Finally, run `main.py` using the following command;
```powershell
python main.py
```