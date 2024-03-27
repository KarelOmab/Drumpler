import os
import sys
import sqlite3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json  # Add this import if it's not already present


class Noggin:
    def __init__(self, host='127.0.0.1', port=5000, debug=True):
        self.__init_env()
        load_dotenv()  # Load environment variables from .env file
        self.app = Flask(__name__)
        self.DATABASE = 'requests.db'
        self.AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')
        self.host = host
        self.port = port
        self.debug = debug
        self.__setup_routes()
        self.__init_db()

    def __setup_routes(self):
        self.app.add_url_rule('/request', view_func=self.__process_request, methods=['POST'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__get_request, methods=['GET'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__update_request, methods=['PUT'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__delete_request, methods=['DELETE'])

    def __get_db_connection(self):
        conn = sqlite3.connect(self.DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def __init_env(self):
        if not os.path.exists(".env"):
            sys.exit("ERROR! You must create a .env file that contains a single line 'AUTHORIZATION_KEY=YourAuthorizationKeyHere'")

    def __init_db(self):
        with self.__get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_ip TEXT,
                    user_agent TEXT,
                    method TEXT,
                    request_url TEXT,
                    request_raw TEXT,
                    is_handled INTEGER DEFAULT 0
                );
            ''')

    def __authorize_request(self):
        authorization = request.headers.get('Authorization')
        return authorization and authorization == f"Bearer {self.AUTHORIZATION_KEY}"

    def __process_request(self):
        if not self.__authorize_request():
            return jsonify({"error": "Invalid or missing authorization"}), 401

        # Extracting additional request data dynamically
        source_ip = request.remote_addr
        user_agent = request.user_agent.string
        method = request.method
        request_url = request.url
        request_raw = json.dumps(request.json)  # Convert request JSON payload to a single line string

        # Insert the request into the database
        request_id = self.__insert_request({
            "source_ip": source_ip,
            "user_agent": user_agent,
            "method": method,
            "request_url": request_url,
            "request_raw": request_raw
        })
        return jsonify({"message": "Request processed successfully", "id": request_id}), 200


    def __insert_request(self, data):
        with self.__get_db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO requests (source_ip, user_agent, method, request_url, request_raw)
                VALUES (?, ?, ?, ?, ?);
            ''', (data['source_ip'], data['user_agent'], data['method'], data['request_url'], data['request_raw']))
            conn.commit()
            return cursor.lastrowid
        
    def __get_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"error": "Invalid or missing authorization"}), 401

        with self.__get_db_connection() as conn:
            request = conn.execute('SELECT * FROM requests WHERE id = ?', (request_id,)).fetchone()
            if request:
                request_dict = dict(request)
                try:
                    # Attempt to parse the 'request_raw' field back into a JSON object
                    request_dict['request_raw'] = json.loads(request_dict['request_raw'])
                except json.JSONDecodeError:
                    # If parsing fails, keep the original string to avoid breaking the response
                    pass
                return jsonify(request_dict), 200
            else:
                return jsonify({"error": "Request not found"}), 404


    def __update_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"error": "Invalid or missing authorization"}), 401

        data = request.json
        with self.__get_db_connection() as conn:
            cursor = conn.execute('UPDATE requests SET is_handled = ? WHERE id = ?', (data.get('is_handled', 0), request_id))
            if cursor.rowcount == 0:  # No rows were updated, implying the request does not exist
                return jsonify({"error": "Request not found"}), 404
            conn.commit()
        return jsonify({"message": "Request updated successfully"}), 200

    def __delete_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"error": "Invalid or missing authorization"}), 401

        with self.__get_db_connection() as conn:
            cursor = conn.execute('DELETE FROM requests WHERE id = ?', (request_id,))
            if cursor.rowcount == 0:  # No rows were deleted, implying the request does not exist
                return jsonify({"error": "Request not found"}), 404
            conn.commit()
        return jsonify({"message": "Request deleted successfully"}), 200

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)

if __name__ == '__main__':
    noggin = Noggin()
    noggin.run()
