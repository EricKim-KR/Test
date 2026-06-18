## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2026-05-07 - [Parallelized Real Estate Crawler]
**Learning:** For web scrapers using Selenium, significant speedup can be achieved by parallelizing independent search tasks (e.g., different property types) using `ThreadPoolExecutor`. Each thread MUST manage its own WebDriver instance to ensure thread safety.
**Action:** Parallelize independent scraping tasks by launching multiple browser instances, while being mindful of system memory limits.

## 2026-05-07 - [Selenium Driver Resolution on Linux]
**Learning:** `webdriver-manager` can sometimes return a path to a non-executable metadata file (e.g., `THIRD_PARTY_NOTICES.chromedriver`) on Linux. A robust crawler must detect this, locate the actual binary in the same directory, and ensure it has executable permissions via `os.chmod`.
**Action:** Always verify the returned `driver_path` from `ChromeDriverManager().install()` and apply necessary fixes for Linux environments to ensure reliable browser initialization.

## 2026-05-14 - [Centralized Driver Setup & WebDriverWait]
**Learning:** Initializing  independently in multiple threads can cause race conditions and redundant network/disk overhead. Centralizing driver resolution and passing the path to threads is more efficient. Additionally, replacing static  with  for specific selectors (like  or ) significantly reduces latency for both successful and empty searches.
**Action:** Always resolve singleton resources (like driver paths) before entering parallel loops and prefer dynamic waiting over static sleeps for element interaction.

## 2026-05-14 - [Centralized Driver Setup & WebDriverWait]
**Learning:** Initializing ChromeDriverManager independently in multiple threads can cause race conditions and redundant network/disk overhead. Centralizing driver resolution and passing the path to threads is more efficient. Additionally, replacing static time.sleep() with WebDriverWait for specific selectors (like li.item or .no_result) significantly reduces latency for both successful and empty searches.
**Action:** Always resolve singleton resources (like driver paths) before entering parallel loops and prefer dynamic waiting over static sleeps for element interaction.
