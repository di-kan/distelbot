import requests
import os
import telebot
import discord
from bs4 import BeautifulSoup
from collections import namedtuple
from dotenv import load_dotenv
import re
from texttable import Texttable
import datetime

Coin = namedtuple("Coin", "name short_name price one_hour twentyfour_hour seven_day volume cap")

def smaller_responses(response):
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
def get_table(coins):
    table = Texttable()
    h_align = ["c" for _ in range(0, 8)]
    v_align = ["m" for _ in range(0, 8)]
    table.set_cols_align(h_align)
    table.set_cols_align(v_align)
    rows = []
    rows.append(["name", "short", "price", "1 h", "24 h", "7 day", "volume", "cap"])
    for coin in coins:
        rows.append(list(coin))
    table.add_rows(rows)
    final_string = f"```\n{table.draw()}\n```"
    return final_string


def update_coins(forced=False):
    global previous_time, interval_minutes, coins

    def refresh_data():
        print("refreshing data from website")
        headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/98.0.4758.102 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"}
        new_coins = []
        try:
            response = requests.get(url, headers=headers, proxies=proxy_servers)
            response.raise_for_status()
            print(response)
        except Exception as e:
            print(f"ERROR: {e}")
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("table", class_="table")
            rows = result.findAll("tr")


            for row in rows:
                tmp = []
                for cell in row.findAll('td'):
                    tmp.append(cell.text.strip())
                if len(tmp) > 0:
                    start = 2
                    new_lines = tmp[start].count('\n')
                    what = "\n"*(new_lines-1)
                    names = re.sub(what, "\n", tmp[start]).split("\n")
                    name = names[0]
                    short_name = names[2]
                    # print(name, short_name)
                    coin = Coin(name, short_name, tmp[start+1],tmp[start+2],tmp[start+3],tmp[start+4],tmp[start+5],tmp[start+6])
                    new_coins.append(coin)
        finally:
            when = datetime.datetime.now()
            return when, new_coins

    if forced:
        print(previous_time)
        when, coins = refresh_data()
        previous_time = when
        print(previous_time)
    else:
        if (datetime.datetime.now() <= datetime.timedelta(minutes=interval_minutes)+previous_time):
            print(f"coins available:{len(coins)}. Will not refresh now")
        else:
            when, coins = refresh_data()
            previous_time = when

def telegram_bot():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)


    @bot.message_handler(commands=['list'])
    def send_all_coin_names(message):
        the_list = "coin1, coin2, coin3"
        bot.reply_to(message, the_list)


    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Howdy, how are you doing?")


    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error:{e}")

def discord_bot():
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD = os.getenv("DISCORD_GUILD")
    intents = discord.Intents(messages=True, message_content=True)
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        # if message is coming from a user and not this bot
        if message.author != client.user:
            match message.content.lower():
                case "/help":
                    response = "/help: shows this command help\n"
                    response += "/print: shows all information\n"
                    response += "/coins: shows all available coins\n"
                    response += "/coins2: shows short names of available coins\n"
                    response += "/<name>: shows coin information of <name>\n"
                    response += "/top10: shows top 10 coins\n"
                    response += "/age: shows when the site was scrapped\n"
                    response += "/update: forces updated of coin data."
                case "/print":
                    response = get_table(coins)
                case "/coins":
                    update_coins()
                    response = ", ".join([coin.name for coin in coins])
                case "/coins2":
                    update_coins()
                    response = ", ".join([coin.short_name for coin in coins])
                case "/update":
                    update_coins(forced=True)
                    response = "Data just updated"
                case "/top10":
                    update_coins()
                    response = get_table(coins[0:10])
                case "/age":
                    update_coins()
                    try:
                        when = (datetime.datetime.now()-previous_time).total_seconds()/60
                    except:
                        when = -1
                    response = f"Website was scrapped {when:.1f} minutes ago. Use /update to rescan. " \
                               f"Updates automatically every 10 minutes"
                case _:
                    update_coins()
                    wanted = message.content.lower()[1:]
                    available = [coin.name.lower() for coin in coins]
                    short_available = [coin.short_name.lower() for coin in coins]
                    if wanted in available:
                        response = str(coins[available.index(wanted)])
                    elif wanted in short_available:
                        tmp_coins = [coins[short_available.index(wanted)]]
                        response = get_table(tmp_coins)
                        print(response)
                    else:
                        response = "Wrong command. Type /help to review syntax"
            responses = smaller_responses(response)
            for response in responses:
                print(len(response))
                await message.channel.send(response)

    @client.event
    async def on_ready():
        guild = discord.utils.get(client.guilds, name=GUILD)
        print(GUILD)
        if guild:
            print(f"{client.user} is connected to the following guild:\n"
                  f"{guild.name}(id:{guild.id}")
            members = '\n - '.join([member.name for member in guild.members])
            print(f"Guild Members:\n - {members}")
        else:
            print(f"{client.user} not connected to any server/guild")
    try:
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error {e}")


ip = '210.230.238.153'
port ='443'
proxy_servers = {
    'http': f'http://{ip}{port}',
    'https': f'http://{ip}:{port}',
}

previous_time = datetime.datetime.now()
interval_minutes = 10
url="https://www.coingecko.com/"
load_dotenv()
coins = []

update_coins(forced=True)
discord_bot()
