## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.

## 2026-05-22 - [Thread-Safe Selenium Parallelization]
**Learning:** When parallelizing Selenium crawlers using `ThreadPoolExecutor`, `ChromeDriverManager().install()` must be called in the main thread. `webdriver-manager` is not thread-safe and concurrent calls to `install()` cause race conditions and file system errors. Passing the pre-installed `driver_path` to workers ensures stability.
**Action:** Always perform environment setup (like driver installation) once in the main thread before spawning worker threads that rely on shared binaries.
