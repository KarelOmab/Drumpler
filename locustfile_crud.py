#locust -f locustfile_crud.py

from locust import HttpUser, task, between
import random

class NogginUser(HttpUser):
    wait_time = between(1, 2)
    authorization_key = 'Bearer YourAuthorizationKeyHere'

    @task
    def get_request(self):
        request_id = random.randint(1, 100)  # Example range, adjust based on your data
        self.client.get(f"/request/{request_id}", headers={'Authorization': self.authorization_key})

    @task
    def update_request(self):
        request_id = random.randint(1, 100)
        payload = {"is_handled": 1}
        self.client.put(f"/request/{request_id}", json=payload, headers={'Authorization': self.authorization_key})

    @task
    def delete_request(self):
        request_id = random.randint(1, 100)
        self.client.delete(f"/request/{request_id}", headers={'Authorization': self.authorization_key})
