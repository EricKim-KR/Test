import time
from Real_estate_crawler.crawler import crawl_properties
import logging

# Disable logging for benchmark
logging.getLogger('Real_estate_crawler.crawler').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)

def benchmark():
    print("Starting benchmark...")
    start_time = time.time()

    # Test with two property types to trigger parallel crawling
    results = crawl_properties(
        city="서울시",
        district="강남구",
        dong="개포동",
        property_types=['APT', 'VILLA']
    )

    end_time = time.time()
    duration = end_time - start_time

    print(f"Benchmark completed in {duration:.2f} seconds")
    print(f"Found {len(results)} properties")
    return duration

if __name__ == "__main__":
    benchmark()
