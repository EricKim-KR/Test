import time
import sys
import os

# Add the current directory to sys.path to import crawler
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import crawl_properties

def benchmark():
    print("Starting benchmark for Real Estate Crawler...")

    city = "서울"
    district = "강남구"
    dong = "개포동"
    property_types = ["APT", "VILLA"]

    start_time = time.time()

    print(f"Crawling {property_types} in {city} {district} {dong}...")
    results = crawl_properties(
        city=city,
        district=district,
        dong=dong,
        property_types=property_types
    )

    end_time = time.time()
    duration = end_time - start_time

    print("-" * 30)
    print(f"Benchmark Results:")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Total items found: {len(results)}")
    print("-" * 30)

    return duration, len(results)

if __name__ == "__main__":
    benchmark()
