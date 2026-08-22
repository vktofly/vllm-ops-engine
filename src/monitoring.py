from prometheus_client import Counter, Histogram, Gauge

# Request latency tracking
REQUEST_LATENCY = Histogram(
    "vllm_request_latency_seconds",
    "Latency of generation requests",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Token throughput tracking
TOTAL_TOKENS_GENERATED = Counter(
    "vllm_total_tokens_generated",
    "Total number of tokens generated"
)

# Queue depth / Active requests
ACTIVE_REQUESTS = Gauge(
    "vllm_active_requests",
    "Number of requests currently being processed"
)
