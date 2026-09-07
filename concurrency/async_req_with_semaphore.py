import argparse
import asyncio

import aiohttp
from tqdm import tqdm


async def worker(
    req_id: int,
    worker_ids: asyncio.Queue,
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    prog_bar: tqdm,
    inflight_bar: tqdm,
):
    async with semaphore:
        inflight_bar.update(1)
        worker_id = await worker_ids.get()
        try:
            prog_bar.write(f"Request {req_id} handled by: worker {worker_id}")
            # execute I/O request - simulates session.get(...)
            # await asyncio.sleep(delay=random.uniform(1, 5))
            async with session.get(f"/req_id{req_id}-worker_id{worker_id}") as _:
                # data = await response.json()
                prog_bar.update(1)
                prog_bar.write(f"Request {req_id} completed by: worker {worker_id}")
        finally:
            worker_ids.put_nowait(worker_id)  # safe because worker_ids is unlimited
            inflight_bar.update(-1)


async def main(
    semaphore: asyncio.Semaphore, num_workers: int, total_requests: int = 100
) -> None:
    session = aiohttp.ClientSession(base_url="http://localhost:8000")

    prog_bar = tqdm(total=total_requests)
    inflight_bar = tqdm(
        total=num_workers,
        desc="In flight",
        position=1,
        leave=False,
    )

    # semaphore approach
    worker_ids = asyncio.Queue()
    for i in range(1, num_workers + 1):
        await worker_ids.put(i)
    async with session:
        work = [
            worker(
                req_id=i,
                worker_ids=worker_ids,
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
