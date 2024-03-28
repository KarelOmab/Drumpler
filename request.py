class Request:
    def __init__(self, id, timestamp, source_ip, user_agent, method, request_url, request_raw, is_handled):
        self._id = id
        self._timestamp = timestamp
        self._source_ip = source_ip
        self._user_agent = user_agent
        self._method = method
        self._request_url = request_url
        self._request_raw = request_raw
        self._is_handled = is_handled

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
    def is_handled(self):
        return self._is_handled

    @is_handled.setter
    def is_handled(self, value):
        self._is_handled = value
