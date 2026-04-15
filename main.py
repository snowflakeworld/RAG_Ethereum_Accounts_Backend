import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from core.rag import RAG
from core.ethereum import process_collection_task, process_specific_block
from core.mysql import get_variable, update_variable

load_dotenv()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserPrompt(BaseModel):
    prompt: str


api_key = os.getenv("OPENAI_API_KEY")
rag_instance = RAG(api_key)


# Create a scheduler instance
scheduler = BackgroundScheduler()


# Function to be called by the cron job
def my_cron_job():
    print("Cron job executed at", time.strftime("%Y-%m-%d %H:%M:%S"))
    last_block_number = int(str(get_variable("blockNumber"))) + 1
    process_specific_block(last_block_number + 1)
    update_variable("blockNumber", last_block_number + 1)
    print(f"Block number: {last_block_number + 1} processed")


# Start the scheduler and add the cron job
def start_scheduler():
    scheduler.add_job(my_cron_job, "interval", seconds=300)  # runs every 5 mins
    scheduler.start()


# Start scheduler when FastAPI app starts
@app.on_event("startup")
async def startup_event():
    start_scheduler()


# FastAPI route to check status of the cron job
@app.get("/")
def read_root():
    return {"message": "FastAPI with cron job is running!"}


# Generate answer about user prompt using RAG
@app.post("/generate")
async def generate_result(input: UserPrompt):
    result = rag_instance.generate(input.prompt)

    if result == None:
        return {"status": "failure", "message": "Cannot generate answer."}

    return result


@app.get("/collect_transactions")
def collect_transactions():
    process_collection_task()
