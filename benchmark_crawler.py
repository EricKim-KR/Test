import time
import logging
from Real_estate_crawler.crawler import crawl_properties

logging.basicConfig(level=logging.ERROR)

def benchmark():
    start_time = time.time()
    print("Starting crawl for Seoul Gangnam-gu Yeoksam-dong...")
    results = crawl_properties("서울시", "강남구", "역삼동", property_types=['APT', 'VILLA'])
    end_time = time.time()

    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Total properties found: {len(results)}")

if __name__ == "__main__":
    benchmark()
