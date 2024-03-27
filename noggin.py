from flask import Flask, request, jsonify
import sqlite3
import threading

app = Flask(__name__)

# Database setup
DATABASE = 'requests.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                authorization TEXT,
                source_ip TEXT,
                user_agent TEXT,
                method TEXT,
                request_url TEXT,
                request_raw TEXT,
                is_handled INTEGER DEFAULT 0
            );
        ''')

def insert_request(data):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            INSERT INTO requests (authorization, source_ip, user_agent, method, request_url, request_raw)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (data['authorization'], data['source_ip'], data['user_agent'], data['method'], data['request_url'], data['request_raw']))
        conn.commit()

@app.route('/process', methods=['POST'])
def process_request():
    required_fields = ['authorization', 'source_ip', 'user_agent', 'method', 'request_url', 'request_raw']
    data = request.json

    # Check for required fields
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Insert request into database
    insert_request(data)

    return jsonify({"message": "Request processed successfully"}), 200

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the Flask app in threaded mode to handle multiple requests
    app.run(debug=True, threaded=True)
