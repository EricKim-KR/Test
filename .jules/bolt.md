## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2026-05-22 - [Thread-Safe Selenium Parallelization]
**Learning:** When parallelizing Selenium crawlers using `ThreadPoolExecutor`, `ChromeDriverManager().install()` must be called in the main thread. `webdriver-manager` is not thread-safe and concurrent calls to `install()` cause race conditions and file system errors. Passing the pre-installed `driver_path` to workers ensures stability.
**Action:** Always perform environment setup (like driver installation) once in the main thread before spawning worker threads that rely on shared binaries.
## 2024-05-28 - [Parallelized Selenium Crawling & Dynamic Waits]
**Learning:** For Selenium-based scrapers, static `time.sleep()` is a major performance killer. Replacing them with `WebDriverWait` (dynamic waits) ensures the script proceeds immediately when the UI is ready. Additionally, parallelizing multi-category searches using `ThreadPoolExecutor` provides significant speedups, but requires careful handling of independent `WebDriver` sessions and pre-locating the driver binary to avoid redundant downloads/checks across threads.
**Action:** Always favor dynamic waits over static sleeps. When parallelizing Selenium, ensure thread-local driver instances and share the driver binary path to optimize startup time.
## 2026-05-22 - [Parallelized Selenium Crawling & Headless Mode]
**Learning:** For web scrapers using Selenium, parallelizing independent requests (like different property types) with `ThreadPoolExecutor` and independent driver instances significantly reduces total execution time. Additionally, `headless=new` mode reduces resource overhead. A critical race condition was avoided by installing the driver once in the main thread and passing the path to workers.
**Action:** Use `ThreadPoolExecutor` for concurrent Selenium tasks, ensuring each thread gets its own `webdriver` instance but shares a pre-resolved `driver_path`. Always use headless mode unless visual debugging is required.
## 2026-05-07 - [Parallelized Real Estate Crawler]
**Learning:** For web scrapers using Selenium, significant speedup can be achieved by parallelizing independent search tasks (e.g., different property types) using `ThreadPoolExecutor`. Each thread MUST manage its own WebDriver instance to ensure thread safety.
**Action:** Parallelize independent scraping tasks by launching multiple browser instances, while being mindful of system memory limits.

## 2026-05-07 - [Selenium Driver Resolution on Linux]
**Learning:** `webdriver-manager` can sometimes return a path to a non-executable metadata file (e.g., `THIRD_PARTY_NOTICES.chromedriver`) on Linux. A robust crawler must detect this, locate the actual binary in the same directory, and ensure it has executable permissions via `os.chmod`.
**Action:** Always verify the returned `driver_path` from `ChromeDriverManager().install()` and apply necessary fixes for Linux environments to ensure reliable browser initialization.

## 2026-05-20 - [Selenium Crawler Bottleneck Reduction]
**Learning:** Replaced fixed `time.sleep()` with `WebDriverWait` and shared a single ChromeDriver binary path across concurrent threads. This reduced parallel crawling time for dual property types (APT & VILLA) by ~50% (from 44s to 22s).
**Action:** Always prefer explicit waits over fixed sleeps and pre-resolve/share expensive environment resources like WebDriver binaries when using parallel executors.
## 2026-06-25 - [Shared ChromeDriver for Parallel Scrapers]
**Learning:** Initializing `ChromeDriverManager().install()` within multiple threads causes race conditions and redundant network calls. Installing it once in the main thread and passing the driver path to worker threads ensures stability and reduces startup overhead.
**Action:** Centralize the driver installation logic when using `ThreadPoolExecutor` with Selenium to avoid race conditions and improve efficiency.

## 2026-06-25 - [Optimized Waits over Fixed Sleep]
**Learning:** Using `time.sleep()` in Selenium scrapers adds guaranteed idle time (e.g., ~6s per crawl), whereas `WebDriverWait` with specific element selectors (including a fast-fail check for "no results") reduces latency significantly while improving reliability.
**Action:** Prefer `WebDriverWait` with targeted lambda conditions (matching multiple possible result states) to minimize wait times and handle dynamic page loading gracefully.
## 2026-05-14 - [Optimized NaverRealEstateCrawler Setup and Latency]
**Learning:** Resolving the driver binary path once in the main thread and passing it to worker threads avoids redundant I/O and network checks by `ChromeDriverManager`. Additionally, removing legacy `time.sleep()` calls in favor of existing `WebDriverWait` significantly reduces idle time during crawling.
**Action:** Pre-calculate setup parameters in the main thread for parallel tasks, and regularly audit for hardcoded delays that can be replaced with event-driven waits.

## 2024-05-29 - [Direct Search URL Navigation]
**Learning:** For web scrapers where the search URL is predictable, navigating directly to the search results page (`https://land.naver.com/search/search.naver?query={keyword}`) is significantly faster than interacting with the UI (typing in a search bar, waiting for suggestions, and clicking). This avoids redundant page loads and complex synchronization with dynamic UI elements.
**Action:** Always investigate if an application supports direct URL parameters for its search or filter functionality to bypass slow UI-based interaction paths.

## 2024-05-28 - [Eager Page Load & Image Disabling]
**Learning:** For data-only scraping where images are not required, setting `page_load_strategy = 'eager'` (waits for `DOMContentLoaded`) and disabling image loading via Chrome preferences significantly reduces total crawl time (e.g., from ~38s to ~12s in this environment). This avoids waiting for slow assets that don't impact the scrape results.
**Action:** Always enable `eager` page load strategy and disable image loading for Selenium crawlers focused on text/data extraction to minimize network overhead and rendering time.
