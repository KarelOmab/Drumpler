import pytest
from flask_testing import TestCase
from noggin import Noggin
from flask import json

class TestNoggin(TestCase):

    def create_app(self):
        app = Noggin(host='127.0.0.1', port=5000, debug=True).app
        app.config['TESTING'] = True
        return app

    def test_authorization_fail(self):
        response = self.client.get('/request/1', headers={'Authorization': 'Bearer WrongKey'})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid or missing authorization", response.json["error"])

    def test_post_request_success(self):
        payload = {
            "foo": "val1",
            "bar": 2,
            "flag": True
        }
        response = self.client.post('/request', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'}, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Request processed successfully", response.json["message"])

    def test_get_nonexistent_request(self):
        response = self.client.get('/request/99999', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(response.status_code, 404)

    def test_successful_get_request(self):
        # Create a request to ensure it exists
        post_payload = {"foo": "val1", "bar": 2, "flag": True}
        post_response = self.client.post('/request', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'}, json=post_payload)
        request_id = post_response.json["id"]
        self.assertEqual(post_response.status_code, 200)

        # Now, retrieve the request
        get_response = self.client.get(f'/request/{request_id}', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json['request_raw'], post_payload)  # Check if the payload matches

    def test_update_nonexistent_request(self):
        payload = {"is_handled": 1}
        response = self.client.put('/request/99999', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'}, json=payload)
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_request(self):
        response = self.client.delete('/request/99999', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(response.status_code, 404)

    def test_crud_lifecycle(self):
        # Create
        post_payload = {"foo": "new", "bar": 3, "flag": False}
        post_response = self.client.post('/request', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'}, json=post_payload)
        self.assertEqual(post_response.status_code, 200)
        request_id = post_response.json["id"]

        # Read
        get_response = self.client.get(f'/request/{request_id}', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json['request_raw'], post_payload)  # Ensure stored JSON matches

        # Update
        put_response = self.client.put(f'/request/{request_id}', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'}, json={"is_handled": 1})
        self.assertEqual(put_response.status_code, 200)

        # Delete
        delete_response = self.client.delete(f'/request/{request_id}', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(delete_response.status_code, 200)

        # Confirm Deletion
        confirm_delete_response = self.client.get(f'/request/{request_id}', headers={'Authorization': 'Bearer YourAuthorizationKeyHere'})
        self.assertEqual(confirm_delete_response.status_code, 404)

if __name__ == '__main__':
    pytest.main()
