import pytest
from time import time, sleep
from feed import CoinAPI


def test_feed():
    coin_api = CoinAPI()
    coin_api.interval_minutes = 1/6
    coin_api.start()
    sleep(2)
    coin_api.get_table()