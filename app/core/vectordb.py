import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import json

load_dotenv()
API_KEY = os.getenv("PINECONE_API_KEY")

# Define the name and dimension of your vector index
index_name = "my-ethereum-index"
dimension = 512  # Replace with the dimension size of your embeddings

# Initialize Pinecone with your API key
pc = Pinecone(api_key=API_KEY)

# Create the index
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=dimension,
        vector_type="dense",
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Connect to the created index
index = pc.Index(index_name)


def upsert_records(id, text, cypher, type):
    index.upsert_records(
        "__default__",
        [{"_id": id, "text": text, "cypher": cypher, "type": type}],
    )


def search_records(prompt):
    results = index.search(
        namespace="__default__",
        query={"inputs": {"text": prompt}, "top_k": 3},
        fields=["text", "cypher", "type"],
    )

    hits = results["result"]["hits"]

    if len(hits) == 0:
        return None

    relevant_records = []
    has_proper_answer = False

    for hit in hits:
        id = hit["_id"]
        score = hit["_score"]
        text = hit["fields"]["text"]
        cypher = hit["fields"]["cypher"]
        type = hit["fields"]["type"]

        relevant_records.append((id, score, text, cypher, type))
        if score >= 0.25:
            has_proper_answer = True

    if has_proper_answer == False:
        return None

    return relevant_records


def clear_db():
    index.delete(delete_all=True, namespace="__default__")


def construct_db():
    try:
        with open("testcases.json", "r") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")

    for i in range(len(data)):
        text = data[i]["text"]
        cypher = data[i]["cypher"]
        type = data[i]["type"]

        upsert_records(f"sql#{i + 1}", text, cypher, type)


# construct_db()
# clear_db()
# search_records(
#     "What is the total amount of Ether sent from 0x123123123123 to 0x123123123123"
# )
