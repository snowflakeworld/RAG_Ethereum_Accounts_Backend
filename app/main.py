import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.core.rag import RAG

load_dotenv()
app = FastAPI()


class UserPrompt(BaseModel):
    prompt: str


rag_instance = None


@app.get("/")
def read_root():
    return {"Hello": "Word"}


@app.get("/initialize")
async def initialize_rag():
    api_key = os.getenv("OPENAI_API_KEY")
    global rag_instance
    rag_instance = RAG(api_key)

    return {"status": "success"}


@app.post("/generate")
async def generate_result(input: UserPrompt):
    if rag_instance == None:
        return {"status": "failure", "message": "RAG instance is not initialized."}

    result = rag_instance.generate(input.prompt)

    if result == None:
        return {"status": "failure", "message": "Cannot generate answer."}

    return result
