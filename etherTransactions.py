import requests
import datetime
from tqdm import tqdm

API_KEY = "3U9QXKB7SQ3UDBRYJM7244FD3RH9QYMR5J"


def get_block_by_timestamp(timestamp):
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainId": 1,
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": int(timestamp),
        "closest": "after",
        "apiKey": API_KEY,
    }
    return requests.get(url, params=params).json()


def get_block(block_number):
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainId": 1,
        "module": "proxy",
        "action": "eth_getBlockByNumber",
        "tag": hex(block_number),
        "boolean": "true",
        "apikey": API_KEY,
    }
    return requests.get(url, params=params).json()


def extract_addresses(block):
    addresses = []

    for tx in block["result"]["transactions"]:
        print(
            tx["from"],
            tx["to"],
            float(int(tx["value"], 16) / 1e18),
            int(tx["blockTimestamp"], 16),
        )
        # print(tx)
        if tx["from"]:
            addresses.append(tx["from"])
        if tx["to"]:
            addresses.append(tx["to"])

    return addresses


ts_2025 = int(datetime.datetime(2026, 4, 12).timestamp())

start_block = int(get_block_by_timestamp(ts_2025)["result"])
print("Start block:", start_block)

end_block = start_block + 1

for block_num in tqdm(range(start_block, end_block)):
    block = get_block(block_num)

    if "result" not in block:
        continue

    timestamp = int(block["result"]["timestamp"], 16)
    addresses = extract_addresses(block)

    # for addr in addresses:
    #     print(f"Address: {addr}")
