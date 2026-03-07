import asyncio
import argparse
import aiohttp
from tqdm import tqdm


async def worker(
    req_id: int,
    worker_ids: asyncio.Queue,
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    prog_bar: tqdm,
):
    # response: ResponseModel | None = None

    async with semaphore:
        worker_id = await worker_ids.get()
        prog_bar.write(f"Request {req_id} handled by: worker {worker_id}")
        # execute I/O request - simulates session.get(...)
        # await asyncio.sleep(random.uniform(1, 5))
        async with session.get("/") as response:
            # data = await response.json()
            prog_bar.update(1)
            prog_bar.write(f"Request {req_id} completed by: worker {worker_id}")
        worker_ids.put_nowait(worker_id)


async def main(
    semaphore: asyncio.Semaphore, num_workers: int, total_requests: int = 100
) -> None:
    session = aiohttp.ClientSession(base_url="http://localhost:8000")

    prog_bar = tqdm(total=total_requests)

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
            )
            for i in range(1, total_requests + 1)
        ]
        await asyncio.gather(*work)

    prog_bar.close()

    return


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
