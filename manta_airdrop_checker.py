from time import sleep
import random
from sys import stderr
import json

from fake_useragent import UserAgent
import requests
from pyfiglet import Figlet
from loguru import logger

import config

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>")

ua = UserAgent(os='windows', browsers=['chrome'])

f = Figlet(font='5lineoblique')
print(f.renderText('Busher'))
print('Telegram channel: @CryptoKiddiesClub')
print('Telegram chat: @CryptoKiddiesChat')
print('Twitter: @CryptoBusher\n')


def check_airdrop(_evm_wallet: str, _dot_wallet: str, proxy: str = None):
    url = 'https://np-api.newparadigm.manta.network/getPointsV1'

    headers = {
        'authority': 'np-api.newparadigm.manta.network',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'uk',
        'content-type': 'application/json',
        'origin': 'https://airdrop.manta.network',
        'referer': 'https://airdrop.manta.network/',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': ua.random,
    }

    json_data = {
        'address': _evm_wallet,
        'polkadot_address': _dot_wallet,
    }

    if proxy:
        _proxies = {
            "http": proxy,
            "https": proxy
        }
        response = requests.post(url, proxies=_proxies, headers=headers, json=json_data)
    else:
        response = requests.post(url, headers=headers, json=json_data)

    json_response = json.loads(response.text)
    message = f'Wallet: {_evm_wallet}:{dot_wallet} - '
    is_eligible = json_response['data']['total_score'] > 0

    if is_eligible:
        message += 'ELIGIBLE'
    else:
        message += 'not eligible'

    if config.LOG_FULL_SERVER_RESPONSE:
        message += f', response: {json_response}'

    if is_eligible:
        logger.success(message)
    else:
        logger.info(message)


def fetch_sleep():
    delay = random.uniform(config.MIN_FETCH_DELAY_SEC, config.MAX_FETCH_DELAY_SEC)
    sleep(delay)


if __name__ == "__main__":
    with open("wallets.txt", "r") as file:
        wallets = [w.strip() for w in file]

    try:
        with open("proxies.txt", "r") as file:
            proxies = [p.strip() for p in file]
    except FileNotFoundError:
        proxies = []

    for i, wallet in enumerate(wallets):
        if len(wallet.split('|')) == 2:
            evm_wallet, dot_wallet = wallet.split('|')
        else:
            evm_wallet = wallet
            dot_wallet = ""

        try:
            check_airdrop(evm_wallet, dot_wallet, proxies[i])
        except IndexError:
            check_airdrop(evm_wallet, dot_wallet)
        except Exception as e:
            logger.error(f'Failed to check wallet {wallet}, reason: {e}')
        finally:
            fetch_sleep()
