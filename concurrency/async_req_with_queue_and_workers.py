import argparse
import asyncio

import aiohttp
from tqdm import tqdm


async def worker(
    worker_id: int,
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    prog_bar: tqdm,
    inflight_bar: tqdm,
):

    while not queue.empty():
        req_id = await queue.get()
        inflight_bar.update(1)
        try:
            prog_bar.write(f"Request {req_id} handled by: worker {worker_id}")

            # execute I/O request - simulates session.get(...)
            # await asyncio.sleep(random.uniform(1, 5))
            async with session.get(f"/req_id{req_id}-worker_id{worker_id}") as _:
                # data = await response.json()
                prog_bar.update(1)
                prog_bar.write(f"Request {req_id} completed by: worker {worker_id}")
        finally:
            queue.task_done()
            inflight_bar.update(-1)


async def main(num_workers: int, total_requests: int = 100) -> None:
    session = aiohttp.ClientSession(base_url="http://localhost:8000")

    prog_bar = tqdm(total=total_requests)
    inflight_bar = tqdm(
        total=num_workers,
        desc="In flight",
        position=1,
        leave=False,
    )

    # queue + worker approach
    q = asyncio.Queue()
    for i in range(1, total_requests + 1):
        await q.put(i)

    async with session:
        work = [
            worker(
                worker_id=i + 1,
                queue=q,
                session=session,
                prog_bar=prog_bar,
                inflight_bar=inflight_bar,
            )
            for i in range(num_workers)
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

    try:
        asyncio.run(main(MAX_CONCURRENT_REQUESTS))
    except KeyboardInterrupt as e:
        print(e)
