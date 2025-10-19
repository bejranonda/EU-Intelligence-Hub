"""Load testing suite using Locust."""
import random
import string
from locust import HttpUser, task, between, events
import logging

logger = logging.getLogger(__name__)

# Sample data for testing
KEYWORDS = ["covid", "economy", "climate", "technology", "healthcare", "education", "politics"]
SEARCH_QUERIES = ["latest news", "trending topics", "market analysis", "tech trends", "health update"]


class APIUser(HttpUser):
    """Load testing user for API endpoints."""

    wait_time = between(1, 3)

    def on_start(self):
        """Setup for each user."""
        self.keyword_ids = []
        self.fetch_initial_keywords()

    def fetch_initial_keywords(self):
        """Fetch initial keywords for later use."""
        response = self.client.get("/api/keywords/?skip=0&limit=10", name="/api/keywords (initial)")
        if response.status_code == 200:
            keywords = response.json()
            self.keyword_ids = [kw.get("id") for kw in keywords.get("data", []) if kw.get("id")]

    @task(3)
    def list_keywords(self):
        """List keywords - most common operation."""
        skip = random.randint(0, 50)
        limit = random.choice([10, 25, 50])
        self.client.get(
            f"/api/keywords/?skip={skip}&limit={limit}",
            name="/api/keywords/?skip=PARAM&limit=PARAM"
        )

    @task(2)
    def search_semantic(self):
        """Perform semantic search."""
        query = random.choice(SEARCH_QUERIES)
        self.client.get(
            f"/api/search/semantic?q={query}",
            name="/api/search/semantic?q=PARAM"
        )

    @task(2)
    def search_keywords(self):
        """Search for keywords."""
        keyword = random.choice(KEYWORDS)
        self.client.get(
            f"/api/keywords/?skip=0&limit=10&name={keyword}",
            name="/api/keywords/?skip=0&limit=10&name=PARAM"
        )

    @task(1)
    def get_keyword_detail(self):
        """Get details of a specific keyword."""
        if self.keyword_ids:
            keyword_id = random.choice(self.keyword_ids)
            self.client.get(
                f"/api/keywords/{keyword_id}",
                name="/api/keywords/[id]"
            )

    @task(1)
    def get_sentiment_trend(self):
        """Get sentiment trend for a keyword."""
        if self.keyword_ids:
            keyword_id = random.choice(self.keyword_ids)
            self.client.get(
                f"/api/sentiment/keywords/{keyword_id}/sentiment",
                name="/api/sentiment/keywords/[id]/sentiment"
            )

    @task(1)
    def get_suggestions(self):
        """Get keyword suggestions."""
        self.client.get("/api/suggestions/?skip=0&limit=10", name="/api/suggestions/")

    @task(1)
    def create_suggestion(self):
        """Create a new keyword suggestion."""
        suggestion_text = "".join(random.choices(string.ascii_letters, k=10))
        self.client.post(
            "/api/suggestions/",
            json={"keyword": suggestion_text, "category": "general"},
            name="/api/suggestions/ (POST)"
        )

    @task(1)
    def health_check(self):
        """Check application health."""
        self.client.get("/health", name="/health")

    @task(1)
    def api_status(self):
        """Check API status."""
        self.client.get("/api/status", name="/api/status")


class StressTestUser(HttpUser):
    """Aggressive load testing user for stress testing."""

    wait_time = between(0.5, 1.5)

    @task(5)
    def rapid_searches(self):
        """Perform rapid sequential searches."""
        for _ in range(5):
            query = random.choice(SEARCH_QUERIES)
            self.client.get(
                f"/api/search/semantic?q={query}",
                name="/api/search/semantic (stress)",
                timeout=10
            )

    @task(5)
    def concurrent_list_requests(self):
        """Multiple concurrent list requests."""
        self.client.get("/api/keywords/?skip=0&limit=100", name="/api/keywords/ (stress)")


# Event handlers for monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    logger.info("=" * 60)
    logger.info("Load Test Started")
    logger.info(f"Target: {environment.host}")
    logger.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    logger.info("=" * 60)
    logger.info("Load Test Completed")
    logger.info("=" * 60)

    # Print summary statistics
    stats = environment.stats
    print("\n" + "=" * 60)
    print("LOAD TEST SUMMARY")
    print("=" * 60)
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"\nResponse Times (ms):")
    print(f"  Min: {stats.total.min_response_time:.0f}")
    print(f"  Max: {stats.total.max_response_time:.0f}")
    print(f"  Avg: {stats.total.avg_response_time:.0f}")
    print(f"  Median: {stats.total.median_response_time:.0f}")
    print(f"  95th percentile: {stats.total.get_response_time_percentile(0.95):.0f}")
    print(f"  99th percentile: {stats.total.get_response_time_percentile(0.99):.0f}")
    print("\n" + "=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Log individual requests (sampling)."""
    if exception:
        logger.error(f"{request_type} {name}: {exception}")


if __name__ == "__main__":
    print("Run with: locust -f locustfile.py --host=http://localhost:8000")
