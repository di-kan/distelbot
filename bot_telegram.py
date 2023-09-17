import logging
from threading import Thread
import datetime
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TelBot:
    def __init__(self, coins, TOKEN):
        self.TOKEN = TOKEN
        self.coins = coins
        self.help_msg = "Invalid command. Type /help for instructions"
        self.application = ApplicationBuilder().token(self.TOKEN).build()
        self.application.add_handler(CommandHandler("help", self.show_help))
        self.application.add_handler(CommandHandler("search", self.search))
        self.application.add_handler(CommandHandler("get", self.get_rates))
        self.application.add_handler(CommandHandler("top10", self.top10))
        self.application.add_handler(CommandHandler("age", self.age))
        self.application.run_polling()
        # self.thread = Thread(target=self.application.run_polling)
        # self.thread.daemon = True
        # self.thread.start()

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = "/help: shows this command help\n"
        response += "/search <string>: if <string> is missing, returns all coins\n"
        response += "/get <name1> <name2>...: shows coin information of all input names\n"
        response += "/top10: shows top 10 coins\n"
        response += "/age: shows when the site was scrapped\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        coins = self.coins.search(update.message.text)
        response = self.help_msg
        if coins:
            coin_names = [coin.other for coin in coins]
            response = ", ".join(coin_names)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    async def get_rates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = self.help_msg
        coins = self.coins.get_rates(update.message.text)
        if coins:
            response = ""
        for coin in coins:
            base = coin.base
            last_date = coin.time
            response += f"{coin.other}:\t{coin.rate:,.6f}€\n"
        response += f"Base:{base} ({last_date})"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    async def top10(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = self.help_msg
        coins = self.coins.get_top10_rates()
        if coins:
            response = ""
        for coin in coins:
            base = coin.base
            last_date = coin.time
            response += f"{coin.other}:\t{coin.rate:,.6f}€\n"
        response += f"Base: {base} ({last_date})"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    async def age(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            when = (datetime.datetime.now()-self.coins.updated).total_seconds()/60
        except:
            when = -1
        response = f"Info was updated {when:.1f} minutes ago.\n" \
                    f"Updates automatically every 10 minutes"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)