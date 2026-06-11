## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2026-05-07 - [Parallelized Real Estate Crawler]
**Learning:** For web scrapers using Selenium, significant speedup can be achieved by parallelizing independent search tasks (e.g., different property types) using `ThreadPoolExecutor`. Each thread MUST manage its own WebDriver instance to ensure thread safety.
**Action:** Parallelize independent scraping tasks by launching multiple browser instances, while being mindful of system memory limits.

## 2026-05-07 - [Selenium Driver Resolution on Linux]
**Learning:** `webdriver-manager` can sometimes return a path to a non-executable metadata file (e.g., `THIRD_PARTY_NOTICES.chromedriver`) on Linux. A robust crawler must detect this, locate the actual binary in the same directory, and ensure it has executable permissions via `os.chmod`.
**Action:** Always verify the returned `driver_path` from `ChromeDriverManager().install()` and apply necessary fixes for Linux environments to ensure reliable browser initialization.

## 2026-05-20 - [Selenium Crawler Bottleneck Reduction]
**Learning:** Replaced fixed `time.sleep()` with `WebDriverWait` and shared a single ChromeDriver binary path across concurrent threads. This reduced parallel crawling time for dual property types (APT & VILLA) by ~50% (from 44s to 22s).
**Action:** Always prefer explicit waits over fixed sleeps and pre-resolve/share expensive environment resources like WebDriver binaries when using parallel executors.
