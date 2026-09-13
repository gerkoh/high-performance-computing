"""
Semaphore-based approach for concurrent requests.
A semaphore controls the maximum number of coroutine executions that can hold the semaphore at the same time.
"""

import argparse
import asyncio
import random

import aiohttp
from fastapi import HTTPException
from tqdm import tqdm

MAX_ATTEMPTS = 3
BASE_DELAY_S = 0.5


async def afetch(
    req_id: int,
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    prog_bar: tqdm,
    inflight_bar: tqdm,
):
    for attempt in range(MAX_ATTEMPTS):
        try:
            async with semaphore:
                try:
                    # Update tqdm
                    inflight_bar.update(1)
                    prog_bar.write(f"Attempt {attempt + 1}: Request {req_id} in flight")

                    # Call API
                    params = {"req_id": req_id}
                    async with session.get(url="/", params=params) as resp:
                        resp.raise_for_status()

                    # Update tqdm
                    prog_bar.write(f"Attempt {attempt + 1}: Request {req_id} completed")
                finally:
                    inflight_bar.update(-1)
            prog_bar.update(1)
            return
        except HTTPException, aiohttp.ClientResponseError:
            # Update tqdm
            prog_bar.write(f"Attempt {attempt + 1}: Request {req_id} failed")

            # Raise if exceeded max attempts
            if attempt == MAX_ATTEMPTS - 1:
                raise
            await asyncio.sleep(
                random.uniform(0, min(20.0, BASE_DELAY_S * 2**attempt))
            )  # aws jitter


async def main(
    semaphore: asyncio.Semaphore, max_requests: int, total_requests: int = 100
) -> None:
    session = aiohttp.ClientSession(base_url="http://localhost:8000")

    prog_bar = tqdm(total=total_requests)
    inflight_bar = tqdm(
        total=max_requests,
        desc="In flight",
        position=1,
        leave=False,
    )

    # semaphore approach
    async with session:
        work = [
            afetch(
                req_id=i,
                semaphore=semaphore,
                session=session,
                prog_bar=prog_bar,
                inflight_bar=inflight_bar,
            )
            for i in range(1, total_requests + 1)
        ]
        await asyncio.gather(*work)

    prog_bar.close()
    inflight_bar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Concurrent requests with rate limits",
    )
    parser.add_argument("-c", "--conc-req", type=int, required=True)

    args = parser.parse_args()
    MAX_CONCURRENT_REQUESTS = args.conc_req

    semaphore = asyncio.Semaphore(value=MAX_CONCURRENT_REQUESTS)

    try:
        asyncio.run(main(semaphore, MAX_CONCURRENT_REQUESTS))
    except KeyboardInterrupt as e:
        print(e)
