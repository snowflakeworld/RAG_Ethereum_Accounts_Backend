import os
from dotenv import load_dotenv
from openai import OpenAI

from vectordb import search_records
from memgraph import memgraph_execute_query

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

user_prompt = input("Input text: ")

# Search relevant text in Pinecone vector database
relevant_records = search_records(user_prompt)

if relevant_records == None:
    print("Cannot find suitable query.")
    exit(0)

cypher_list = []
for record in relevant_records:
    cypher_list.append(record[3])
# (id, score, text, cypher, type) = search_records(user_prompt)

# Reconstruct Cypher query using LLM
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """You are a helpful assistant.\nYou should reconstruct a Cypher query and output reconstructed Cypher query according to my input prompt and template Cypher query list.\n
            Inside template query, there might be N, 0xAddress, 0xAddress1, 0xAddress2, 0xTransactionHash and you should replace them using real values extracted from corresponding user prompt.\n
            I will give you up to 3 template Cypher query list and you should select the most relevant query and process with it.
            I need only reconstructed query so the output of this process should be the exact reconstructed query.""",
        },
        {
            "role": "user",
            "content": "This is user prompt:\n"
            + user_prompt
            + "And this is a template Cypher query:\n"
            + str(cypher_list),
        },
    ],
)

real_cypher_content = completion.choices[0].message.content
real_cypher_query = (
    real_cypher_content.replace("```", "").replace("cypher", "").replace("Cypher", "")
)

# print(real_cypher_query)

query_results = memgraph_execute_query(real_cypher_query)

# print(query_results)

# Make humanized and meaningful answer using LLM
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """You are a helpful assistant.\nYou should output a plain user-friendly English sentences to represent ethereum accounts and transactions.\n
            The input text consists of inputted user prompt and the result of the memgraph Cypher query according to the user prompt.\n
            In the result of the memgraph Cypher query, there might be fields like one of these\n
            'totalTransactionCount'(number of transactions), 'totalTransactionAmount'(sum of amount of transactions in Ether), 'accountBalance'(balance of the Ethereum account in Ether),\t
            'totalSentAmount'(sum of transferred amounts in Ether), 'transactionCount'(number of transactions), 'totalReceivedAmount'(sum of received amounts in Ether),\t
            'transactionAmount'(sum of amount of transactions in Ether), 'transactionType'(whether transaction type 'Sent' or 'Received'),\t
            'transactionHash'(hash value of Ethereum transaction), 'value'(amount of Ethereum transaction in Ether), 'timestamp'(block timestamp of a transaction),\t
            'gas'(used gas of a Ethereum transaction), 'blockNumber'(block number which contains the transaction), 'transactionIndex'(index of the transaction inside the block)\n\n
            You should recognize user prompt and memgraph Cypher query execution results and generate user-friendly sentences that represents answers for user prompt.
            I need generated English sentences only.""",
        },
        {
            "role": "user",
            "content": "This is user prompt:\n"
            + user_prompt
            + "And this is a result of memgraph Cypher query execution:\n"
            + str(query_results),
        },
    ],
)

real_output = completion.choices[0].message.content

print(real_output)
