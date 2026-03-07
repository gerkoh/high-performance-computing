import random
from fastapi import FastAPI
import asyncio
from dataclasses import dataclass

@dataclass
class ResponseModel:
    message: str


app = FastAPI()

@app.get("/")
async def simulate_request():
    await asyncio.sleep(delay=random.uniform(1, 5))
    return ResponseModel(message="ok")
