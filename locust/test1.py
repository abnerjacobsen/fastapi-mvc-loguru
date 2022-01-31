import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    # wait_time = between(1, 5)

    @task(3)
    def ready(self):
        self.client.get("/api/v1/ready")

    @task
    def microservice(self):
        for item_id in range(10):
            self.client.get("/api/v1/microservice")
            # time.sleep(1)
