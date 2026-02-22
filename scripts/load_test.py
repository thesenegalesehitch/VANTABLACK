import asyncio
import aiohttp
import time
import argparse
from statistics import mean, median

async def worker(url, num_requests, session):
    times = []
    errors = 0
    for _ in range(num_requests):
        start = time.perf_counter()
        try:
            async with session.get(url) as response:
                await response.read()
                if response.status >= 400:
                    errors += 1
        except Exception:
            errors += 1
        end = time.perf_counter()
        times.append(end - start)
    return times, errors

async def main():
    parser = argparse.ArgumentParser(description="Vantablack Load Tester")
    parser.add_argument("--url", default="http://localhost:8000/v5/health", help="Target URL")
    parser.add_argument("--c", type=int, default=100, help="Concurrency")
    parser.add_argument("--n", type=int, default=10000, help="Total requests")
    args = parser.parse_args()

    print(f"Starting load test on {args.url}")
    print(f"Concurrency: {args.c}, Total Requests: {args.n}")

    start_time = time.time()
    
    requests_per_worker = args.n // args.c
    
    connector = aiohttp.TCPConnector(limit=args.c)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(args.c):
            tasks.append(worker(args.url, requests_per_worker, session))
        
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    all_times = []
    total_errors = 0
    for t, e in results:
        all_times.extend(t)
        total_errors += e
        
    rps = len(all_times) / total_time
    
    print("\nResults:")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Requests/sec: {rps:.2f}")
    print(f"Total Errors: {total_errors}")
    print(f"Avg Latency: {mean(all_times)*1000:.2f}ms")
    print(f"Median Latency: {median(all_times)*1000:.2f}ms")

if __name__ == "__main__":
    asyncio.run(main())