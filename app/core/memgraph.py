from gqlalchemy import Memgraph

# Connect to Memgraph
memgraph = Memgraph("127.0.0.1", 7687)


# Function to check if node exists
def node_exists(address):
    result = memgraph.execute(
        f"MATCH (n:Account {{address: '{address}'}}) RETURN n LIMIT 1"
    )
    return result and len(result) > 0


# Function to create or update a node
def create_or_update_node(address):
    if not node_exists(address):
        memgraph.execute(f"CREATE (n:Account {{address: '{address}'}})")


# Function to insert transaction and create relationships
def memgraph_insert_transaction(
    from_address,
    to_address,
    value,
    timestamp,
    transaction_index,
    transaction_hash,
    block_hash,
    block_number,
    gas,
    gas_price,
    nonce,
):
    # Create or update nodes
    create_or_update_node(from_address)
    create_or_update_node(to_address)

    # Create the relationship between the addresses (could be "SENT" or "RECEIVED")
    memgraph.execute(
        f"""
    MATCH (from:Account {{address: '{from_address}'}}), (to:Account {{address: '{to_address}'}})
    CREATE (from)-[:SENT]->(tx:Transaction {{value: {value}, timestamp: '{timestamp}', transactionIndex: '{transaction_index}', transactionHash: '{transaction_hash}', blockHash: '{block_hash}', blockNumber: '{block_number}', gas: '{gas}', gasPrice: '{gas_price}', nonce: '{nonce}'}})-[:TO]->(to)
    """
    )


def memgraph_execute_query(query):
    query_results = memgraph.execute_and_fetch(query)
    results = []
    for row in query_results:
        results.append(row)
    return results


# Sample transaction data
# from_address = "0xSenderAddress"
# to_address = "0xReceiverAddress"
# value = 10
# timestamp = "2026-04-12T10:00:00"

# Insert the transaction
# insert_transaction(from_address, to_address, value, timestamp)
