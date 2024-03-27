#locust -f locustfile_post.py

from locust import HttpUser, task, between

class NogginUser(HttpUser):
    wait_time = between(1, 5)  # Simulate users waiting between 1 to 5 seconds between tasks

    @task
    def create_request(self):
        headers = {'Authorization': 'Bearer YourAuthorizationKeyHere'}
        payload = {
            "data": "Sample request data"
        }
        self.client.post("/request", json=payload, headers=headers)
