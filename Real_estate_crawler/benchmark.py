import time
import logging
from crawler import crawl_properties

# Enable logging for debugging
logging.getLogger('crawler').setLevel(logging.INFO)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

def benchmark():
    print("Starting benchmark...")
    start_time = time.time()

    # Use a real search that should return results
    results = crawl_properties("서울", "강남구", "대치동", property_types=['APT', 'VILLA'])

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n--- Benchmark Results ---")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Total properties found: {len(results)}")
    print(f"--------------------------\n")

    return duration

if __name__ == "__main__":
    benchmark()
