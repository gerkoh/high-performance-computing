"""
Queue + worker pool approach for concurrent requests (emulates the producer-consumer pattern).
Spawns workers to repeatedly poll the queue for work to do. Does not require creating coroutine objects for each work item, limiting memory required.
Implement bounded queues with asyncio.Queue(maxsize=...) to limit the number of items it can hold.
    - This addresses the scenario where the producer places items into the queue at a faster rate than the consumer (worker) can process them, potentially triggering OOM.
"""

import argparse
import asyncio
import random

import aiohttp
from fastapi import HTTPException
from tqdm import tqdm

MAX_ATTEMPTS = 3
BASE_DELAY_S = 0.5


async def producer(queue: asyncio.Queue, total_requests: int):
    for i in range(1, total_requests + 1):
        await queue.put((i, 0))  # blocks here when queue is full -> backpressure


async def requeue(queue: asyncio.Queue, req_id: int, attempt: int):
    await asyncio.sleep(
        random.uniform(0, min(20.0, BASE_DELAY_S * 2**attempt))
    )  # aws jitter
    await queue.put((req_id, attempt + 1))
    queue.task_done()


async def worker(
    worker_id: int,
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    prog_bar: tqdm,
    inflight_bar: tqdm,
):
    while True:
        req_id, attempt = await queue.get()
        try:
            try:
                # Update tqdm
                inflight_bar.update(1)
                prog_bar.write(
                    f"Attempt {attempt + 1}: Request {req_id} in flight (worker {worker_id})"
                )

                # Call API
                params = {"req_id": req_id, "worker_id": worker_id}
                async with session.get(url="/", params=params) as resp:
                    resp.raise_for_status()

                # Update tqdm
                prog_bar.write(
                    f"Attempt {attempt + 1}: Request {req_id} completed (worker {worker_id})"
                )
            finally:
                inflight_bar.update(-1)
            queue.task_done()
            prog_bar.update(1)
        except HTTPException, aiohttp.ClientResponseError:
            # Update tqdm
            prog_bar.write(
                f"Attempt {attempt + 1}: Request {req_id} failed (worker {worker_id})"
            )

            # Do not requeue if max attempts reached
            if attempt == MAX_ATTEMPTS - 1:
                prog_bar.write(f"Max attempts reached for request {req_id}")
                queue.task_done()
            else:
                asyncio.create_task(requeue(queue, req_id, attempt))


async def main(
    max_workers: int, queue_size: int = 50, total_requests: int = 100
) -> None:
    session = aiohttp.ClientSession(base_url="http://localhost:8000")

    prog_bar = tqdm(total=total_requests)
    inflight_bar = tqdm(
        total=max_workers,
        desc="In flight",
        position=1,
        leave=False,
    )

    # queue + worker approach
    q = asyncio.Queue(maxsize=queue_size)

    async with session:
        workers = [
            asyncio.create_task(
                worker(
                    worker_id=i + 1,
                    queue=q,
                    session=session,
                    prog_bar=prog_bar,
                    inflight_bar=inflight_bar,
                )
            )
            for i in range(max_workers)
        ]

        producer_task = asyncio.create_task(
            producer(queue=q, total_requests=total_requests)
        )
        await producer_task
        await q.join()  # all items processed (including those requeued)

        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    prog_bar.close()
    inflight_bar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Number of workers",
    )
    parser.add_argument("-c", "--workers", type=int, required=True)

    args = parser.parse_args()
    MAX_CONCURRENT_REQUESTS = args.workers

    try:
        asyncio.run(main(MAX_CONCURRENT_REQUESTS))
    except KeyboardInterrupt as e:
        print(e)
