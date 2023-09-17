import os
from dotenv import load_dotenv
import logging
from bot_telegram import TelBot
from bot_discord import  DiscBot
from feed import CoinAPI


if __name__ == "__main__":
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD = os.getenv("DISCORD_GUILD")

    coins = CoinAPI()
    coins.start()

    disc = DiscBot(coins, DISCORD_TOKEN, GUILD)
    tel = TelBot(coins, BOT_TOKEN)
