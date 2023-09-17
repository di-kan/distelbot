import requests
import pickle
# from texttable import Texttable
from collections import namedtuple
from operator import attrgetter
import os
import json
from time import sleep
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread

Coin = namedtuple("Coin", "base other rate time")

class CoinAPI:
    def __init__(self):
        load_dotenv()
        self.interval_minutes = 10
        self.MY_API = os.getenv("COINAPI")
        self.coins = []
        self.updating = True
        self.updated = datetime.now()
        self.main_loop_thread = Thread(target=self.main_loop)
        self.main_loop_thread.daemon = True

    def start(self):
        self.updating = True
        self.main_loop_thread.start()

    def stop(self):
        self.updating = False

    def main_loop(self):
        while self.updating:
            self.updated, self.coins = self._get_coins()
            print(f"Updated: {self.updated}")
            sleep(self.interval_minutes*60)

    def _fetch_data(self):
        url = 'https://api.exchangerate.host/latest'
        # url = 'https://rest.coinapi.io/v1/exchangerate/BTC?invert=false'
        # headers = {'X-CoinAPI-Key' : self.MY_API}
        # response = requests.get(url, headers=headers)
        response = requests.get(url)
        # print(response2.text)
        return response.text

    def _get_coins(self):
        try:
            text = self._fetch_data()
            js = json.loads(text)

            base = js['base']
            new_coins = []
            rates_dict = js['rates']
            time = js['date']
            for other, rate in rates_dict.items():
                new_coins.append(Coin(base, other, rate, time))
            when = datetime.now()
            new_coins.sort()
        except KeyError as err:
            print(js)
            when = self.updated
            new_coins = self.coins
        return when, new_coins

    def get_rates(self, command):
        # /get eur usd
        arguments = command.split(" ")
        result = []
        if arguments[0].lower() == "/get":
            if len(arguments) > 1:
                wanted_coins = arguments[1:]
                for coin in self.coins:
                    for wanted_coin in wanted_coins:
                        if coin.other.lower() == wanted_coin.lower():
                            result.append(coin)
        return result

    def get_top10_rates(self):
        sorted_coins = sorted(self.coins, key=attrgetter('rate'), reverse=False)
        result = []
        for coin in sorted_coins[0:10]:
            result.append(coin)
        return result

    def search(self, command):
        # /search a
        arguments = command.split(" ")
        result = []
        if arguments[0].lower() == "/search":
            if len(arguments) == 2:
                search_string = arguments[1]
                for coin in self.coins:
                    if search_string.lower() in coin.other.lower():
                        result.append(coin)
            else:
                for coin in self.coins:
                    result.append(coin)
        return result

# coin = CoinAPI()
# coin.start()
# sleep(4)
# print(coin.search("z"))