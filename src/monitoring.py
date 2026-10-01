from prometheus_client import Counter, Gauge, Histogram


class MetricsRegistry:
    """
    Encapsulates all Prometheus metrics.
    Using a class instead of global module state prevents testing conflicts
    and allows for clean dependency injection.
    """

    def __init__(self):
        self.request_latency = Histogram(
            "vllm_request_latency_seconds",
            "Latency of generation requests",
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
        )
        self.total_tokens_generated = Counter(
            "vllm_total_tokens_generated", "Total number of tokens generated"
        )
        self.active_requests = Gauge(
            "vllm_active_requests", "Number of requests currently being processed"
        )
