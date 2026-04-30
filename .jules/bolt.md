## 2026-04-30 - [Parallelized Weather API Calls]
**Learning:** In a Flask app where multiple external API calls are made for a single request, using `ThreadPoolExecutor` can nearly halve the response time if the calls are independent. Connection pooling via `requests.Session` further reduces overhead for multiple calls to the same host.
**Action:** Always check for independent I/O-bound tasks that can be parallelized, especially when dealing with external third-party APIs.
