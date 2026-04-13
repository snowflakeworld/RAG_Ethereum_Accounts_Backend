import requests
import datetime
from tqdm import tqdm
from memgraph import insert_transaction

API_KEY = "3U9QXKB7SQ3UDBRYJM7244FD3RH9QYMR5J"


# Get Ethereum Block number by timestamp
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


# Get Ethereum Block data by block number
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


# Get Ethereum transaction history (fromAddress, toAddress, value, timestamp) from block data
def extract_transactions(block):
    transactions = []

    for tx in block["result"]["transactions"]:
        # print(tx)
        # print(
        #     tx["from"],
        #     tx["to"],
        #     float(int(tx["value"], 16) / 1e18),
        #     int(tx["blockTimestamp"], 16),
        # )

        type = int(tx["type"], 16)
        if type != 2:
            continue

        from_address = tx["from"]
        to_address = tx["to"]
        value = float(int(tx["value"], 16) / 1e18)
        timestamp = int(tx["blockTimestamp"], 16)
        transaction_index = int(tx["transactionIndex"], 16)
        transaction_hash = tx["hash"]
        block_hash = tx["blockHash"]
        block_number = int(tx["blockNumber"], 16)
        gas = int(tx["gas"], 16)
        gas_price = float(int(tx["gasPrice"], 16) / 1e9)
        nonce = tx["nonce"]

        if from_address and to_address and value and timestamp:
            transactions.append(
                {
                    "fromAddress": from_address,
                    "toAddress": to_address,
                    "value": value,
                    "timestamp": timestamp,
                    "transactionIndex": transaction_index,
                    "transactionHash": transaction_hash,
                    "blockHash": block_hash,
                    "blockNumber": block_number,
                    "gas": gas,
                    "gasPrice": gas_price,
                    "nonce": nonce,
                }
            )

    return transactions


# Get start and end block number
ts_2025 = int(datetime.datetime(2025, 1, 1).timestamp())
ts_2026 = int(datetime.datetime(2026, 4, 11).timestamp())

start_block = int(get_block_by_timestamp(ts_2025)["result"])
print("Start block:", start_block)
end_block = int(get_block_by_timestamp(ts_2026)["result"])
print("End block:", end_block)

end_block = start_block + 10

# Get transaction history from range(start_block, end_block)
# Insert transaction data into memgraph
for block_num in tqdm(range(start_block, end_block)):
    block = get_block(block_num)

    if "result" not in block:
        continue

    transactions = extract_transactions(block)

    print(block_num, len(transactions))

    idx = 0
    for transaction in transactions:
        insert_transaction(
            transaction["fromAddress"],
            transaction["toAddress"],
            transaction["value"],
            transaction["timestamp"],
            transaction["transactionIndex"],
            transaction["transactionHash"],
            transaction["blockHash"],
            transaction["blockNumber"],
            transaction["gas"],
            transaction["gasPrice"],
            transaction["nonce"],
        )
        # insert_data(transaction[0], transaction[1], transaction[2], transaction[3])
        idx = idx + 1
        print(transaction)

    # Insert transaction data into memgraph
