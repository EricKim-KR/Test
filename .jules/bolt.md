## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2026-05-22 - [Parallelized Selenium Crawling & Headless Mode]
**Learning:** For web scrapers using Selenium, parallelizing independent requests (like different property types) with `ThreadPoolExecutor` and independent driver instances significantly reduces total execution time. Additionally, `headless=new` mode reduces resource overhead. A critical race condition was avoided by installing the driver once in the main thread and passing the path to workers.
**Action:** Use `ThreadPoolExecutor` for concurrent Selenium tasks, ensuring each thread gets its own `webdriver` instance but shares a pre-resolved `driver_path`. Always use headless mode unless visual debugging is required.
