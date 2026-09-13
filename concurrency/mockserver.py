"""
Run this mock server with: `fastapi run mockserver.py`
"""

import asyncio
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class ResponseModel(BaseModel):
    message: str


app = FastAPI()


@app.get("/")
async def simulate_request(req_id: int | None = None, worker_id: int | None = None):
    await asyncio.sleep(delay=random.uniform(1, 5))  # simulate work done on server
    if random.random() < 0.1:  # simulate server error
        raise HTTPException(
            status_code=500,
            detail=f"Server error experienced for req_id: {req_id}, worker_id: {worker_id}.",
        )
    return ResponseModel(message="ok")
