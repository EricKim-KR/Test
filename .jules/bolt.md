## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2024-05-28 - [Parallelized Selenium Crawling & Dynamic Waits]
**Learning:** For Selenium-based scrapers, static `time.sleep()` is a major performance killer. Replacing them with `WebDriverWait` (dynamic waits) ensures the script proceeds immediately when the UI is ready. Additionally, parallelizing multi-category searches using `ThreadPoolExecutor` provides significant speedups, but requires careful handling of independent `WebDriver` sessions and pre-locating the driver binary to avoid redundant downloads/checks across threads.
**Action:** Always favor dynamic waits over static sleeps. When parallelizing Selenium, ensure thread-local driver instances and share the driver binary path to optimize startup time.
