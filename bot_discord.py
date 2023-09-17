import logging
import discord
import datetime
from threading import Thread
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class DiscBot:
    def __init__(self, coins, DISCORD_TOKEN, DISCORD_GUILD):
        self.TOKEN = DISCORD_TOKEN
        self.GUILD = DISCORD_GUILD
        self.coins = coins
        self.help_msg = "Invalid command. Type /help for instructions"
        self.intents = discord.Intents(messages=True, message_content=True)
        self.client = discord.Client(intents=self.intents)
        self.client.event(self.on_message)
        self.client.event(self.on_ready)
        self.thread = Thread(target=self.main)
        self.thread.daemon = True
        self.thread.start()


    def main(self):
        try:
            self.client.run(self.TOKEN)
        except Exception as e:
            print(f"Error {e}")

    async def on_message(self, message):
        # if message is coming from a user and not this bot
        if message.author != self.client.user and message.content.lower().startswith("/"):
            command = message.content.lower()
            main_command = command.split(" ")[0].lower()
            match main_command:
                case "/help":
                    response = "/help: shows this command help\n"
                    response += "/search <string>: if <string> is missing, returns all coins\n"
                    response += "/get <name1> <name2>...: shows coin information of all input names\n"
                    response += "/top10: shows top 10 coins\n"
                    response += "/age: shows when the site was scrapped\n"
                case "/search":
                    coins = self.coins.search(command)
                    coin_names = [coin.other for coin in coins]
                    response = ", ".join(coin_names)
                case "/get":
                    coins = self.coins.get_rates(command)
                    response = ""
                    for coin in coins:
                        base = coin.base
                        last_date = coin.time
                        response += f"{coin.other}:\t{coin.rate:,.6f}€\n"
                    response += f"Base:{base} ({last_date})"
                case "/top10":
                    coins = self.coins.get_top10_rates()
                    response = ""
                    for coin in coins:
                        base = coin.base
                        last_date = coin.time
                        response += f"{coin.other}:\t{coin.rate:,.6f}€\n"
                    response += f"Base: {base} ({last_date})"
                case "/age":
                    try:
                        when = (datetime.datetime.now()- self.coins.updated).total_seconds()/60
                    except:
                        when = -1
                    response = f"Info was updated {when:.1f} minutes ago.\n" \
                            f"Updates automatically every 10 minutes"
                case _:
                    response = self.help_msg

            responses = self.smaller_responses(response)
            for response in responses:
                if len(response) > 0:
                    # sends response to the chat
                    await message.channel.send(response)

    async def on_ready(self):
        guild = discord.utils.get(self.client.guilds, name=self.GUILD)
        if guild:
            print(f"{self.client.user} is connected to the following guild:\n"
                f"{guild.name}(id:{guild.id}")
            members = '\n - '.join([member.name for member in guild.members])
            print(f"Guild Members:\n - {members}")
        else:
            print(f"{self.client.user} not connected to any server/guild")

    def smaller_responses(self, response):
        if len(response) > 2000:
            results = []
            size = 1700
            response = response[4:-4]
            rows = response.split("\n")
            n = 1+ len(response) // size
            n_rows = len(rows) // n
            for i in range(0, n):
                results.append("\n".join(rows[i*n_rows:n_rows*(i+1)]))
            if n*n_rows < len(rows):
                results.append("\n".join(rows[n*n_rows:]))
            results = [f"```\n{result}\n```" for result in results]
            return results
        else:
            return [response]
