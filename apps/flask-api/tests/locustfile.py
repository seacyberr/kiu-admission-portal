"""
Load testing with Locust.

Install: pip install locust
Run: locust -f tests/load_test.py --host=http://localhost:5001
"""
from locust import HttpUser, task, between


class KIUPortalUser(HttpUser):
    """Simulates a KIU Portal user."""
    wait_time = between(1, 3)

    def on_start(self):
        """Login when user starts."""
        response = self.client.post("/api/auth/login", json={
            "email": "loadtest@example.com",
            "password": "testpass123"
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
        else:
            self.token = None

    @task(3)
    def view_programs(self):
        """View available programs (high frequency)."""
        self.client.get("/api/admission/programs")

    @task(2)
    def view_opportunities(self):
        """View job opportunities."""
        self.client.get("/api/opportunities")

    @task(1)
    def view_career_paths(self):
        """View career paths."""
        self.client.get("/api/career/paths")

    @task(1)
    def health_check(self):
        """Check API health."""
        self.client.get("/api/healthz")


class AdminUser(HttpUser):
    """Simulates an admin user."""
    wait_time = between(2, 5)

    def on_start(self):
        """Login as admin."""
        response = self.client.post("/api/auth/login", json={
            "email": "admin@kiu.ac.ug",
            "password": "admin123"
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
        else:
            self.token = None

    @task(2)
    def view_applications(self):
        """View admission applications."""
        if self.token:
            self.client.get(
                "/api/admission/applications",
                headers={"Authorization": f"Bearer {self.token}"}
            )

    @task(1)
    def view_analytics(self):
        """View analytics dashboard."""
        if self.token:
            self.client.get(
                "/api/admission/analytics",
                headers={"Authorization": f"Bearer {self.token}"}
            )