"""
Run this mock server with: `fastapi run mock-server.py`
"""

import asyncio
import random
from dataclasses import dataclass

from fastapi import FastAPI


@dataclass()
class ResponseModel:
    message: str


app = FastAPI()


@app.get("/req_id{req_id}-worker_id{worker_id}")
async def simulate_request(req_id: int, worker_id: int):
    await asyncio.sleep(delay=random.uniform(1, 5))
    return ResponseModel(message="ok")
