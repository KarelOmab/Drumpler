import requests
import json
from constants import NOGGIN_URL, AUTHORIZATION_KEY

class Request:
    def __init__(self, id, timestamp, source_ip, user_agent, method, request_url, request_raw, is_handled):
        self._id = id
        self._timestamp = timestamp
        self._source_ip = source_ip
        self._user_agent = user_agent
        self._method = method
        self._request_url = request_url
        self._request_raw = request_raw
        self._request_json = json.loads(request_raw)
        self._is_handled = is_handled

    def mark_as_handled(self):
        headers = {
            'Authorization': f'Bearer {AUTHORIZATION_KEY}',
            'Content-Type': 'application/json'  # Indicate JSON payload
        }
        payload = {
            'is_handled': 1  # Assuming setting `is_handled` to 1 marks it as handled
        }

        try:
            response = requests.put(f"{NOGGIN_URL}/request/{self.id}", json=payload, headers=headers)
            if response.status_code == 200:
                return f"Request {self.id} marked as handled successfully."
            else:
                # Attempt to extract and print a more descriptive error message
                try:
                    error_message = response.json().get('message', 'No error message provided.')
                except ValueError:  # If response is not in JSON format
                    error_message = response.text
                return f"Failed to mark request {self.id} as handled: {response.status_code}, Error: {error_message}"
        except requests.exceptions.RequestException as e:
            return f"Error marking request {self.id} as handled: {e}"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def source_ip(self):
        return self._source_ip

    @source_ip.setter
    def source_ip(self, value):
        self._source_ip = value

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value):
        self._user_agent = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def request_url(self):
        return self._request_url

    @request_url.setter
    def request_url(self, value):
        self._request_url = value

    @property
    def request_raw(self):
        return self._request_raw

    @request_raw.setter
    def request_raw(self, value):
        self._request_raw = value

    @property
    def request_json(self):
        return self._request_json

    @request_json.setter
    def request_json(self, value):
        self._request_json = value

    @property
    def is_handled(self):
        return self._is_handled

    @is_handled.setter
    def is_handled(self, value):
        self._is_handled = value
