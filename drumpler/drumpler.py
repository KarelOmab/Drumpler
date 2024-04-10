import os
import sys
from flask import Flask, request, jsonify
from .constants import DRUMPLER_HOST, DRUMPLER_PORT, DRUMPLER_DEBUG, DATABASE_URI, AUTHORIZATION_KEY
import json
from flask_sqlalchemy import SQLAlchemy
from .request import Request as BaseRequest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Request(db.Model, BaseRequest):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    source_ip = db.Column(db.String(128))
    user_agent = db.Column(db.String(256))
    method = db.Column(db.String(8))
    request_url = db.Column(db.String(256))
    request_raw = db.Column(db.Text)
    custom_value = db.Column(db.String(256))
    is_handled = db.Column(db.Integer, default=0)
    is_being_processed = db.Column(db.Boolean, default=False)

class Drumpler:
    def __init__(self):
        self.__init_env()
        self.app = Flask(__name__)
        self.DATABASE = 'requests.db'
        self.AUTHORIZATION_KEY = AUTHORIZATION_KEY

        # Fetching environment variables or using defaults
        self.host = os.environ.get("DRUMPLER_HOST", DRUMPLER_HOST)
        self.port = os.environ.get("DRUMPLER_PORT", DRUMPLER_PORT)
        self.debug = os.environ.get("DRUMPLER_DEBUG",DRUMPLER_DEBUG)
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize SQLAlchemy with the Flask app here instead of global scope
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()  # Move database initialization here
        
        self.__setup_routes()

    def __setup_routes(self):
        self.app.add_url_rule('/', view_func=self.hello_world, methods=['GET'])
        self.app.add_url_rule('/request', view_func=self.__process_request, methods=['POST'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__get_request, methods=['GET'])
        self.app.add_url_rule('/request/next-unhandled', view_func=self.__get_next_unhandled_request, methods=['GET'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__update_request, methods=['PUT'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__delete_request, methods=['DELETE'])

    def __init_env(self):
        if not os.path.exists(".env"):
            sys.exit("ERROR! You must create a .env file that contains a single line 'AUTHORIZATION_KEY=YourAuthorizationKeyHere'")

    def __authorize_request(self):
        authorization = request.headers.get('Authorization')
        return authorization and authorization == f"Bearer {self.AUTHORIZATION_KEY}"
    
    def hello_world(self):
        return "Hello World"

    def __process_request(self):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        data = request.get_json() or {}  # Fallback to an empty dict if no JSON is provided
        custom_value = request.args.get('custom_value', None)

        new_request = Request(
            source_ip=request.remote_addr,
            user_agent=request.user_agent.string,
            method=request.method,
            request_url=request.url,
            request_raw=json.dumps(data),
            custom_value=custom_value
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Request processed successfully", "id": new_request.id}), 200
    
    def __get_next_unhandled_request(self):
        with db.session.begin():
            # Start with a base query
            query = db.session.query(Request)\
                .filter(Request.is_handled == 0, 
                        Request.is_being_processed == False)

            # Conditionally add the custom_value filter if it is provided
            custom_value = request.args.get('custom_value', None)
            if custom_value is not None:
                query = query.filter(Request.custom_value == custom_value)

            # Execute the query with ordering and locking
            unhandled_request = query.order_by(Request.id)\
                .with_for_update(skip_locked=True).first()

            if unhandled_request:
                # Prepare data before committing the transaction
                request_data = {
                    "id": unhandled_request.id,
                    "timestamp": unhandled_request.timestamp.isoformat(),
                    "source_ip": unhandled_request.source_ip,
                    "user_agent": unhandled_request.user_agent,
                    "method": unhandled_request.method,
                    "request_url": unhandled_request.request_url,
                    "request_raw": unhandled_request.request_raw,
                    "custom_value": unhandled_request.custom_value,  # Include the custom field in the response
                    "is_handled": unhandled_request.is_handled
                }

                # Mark the request as being processed
                unhandled_request.is_being_processed = True
                # Commit is done by the context manager upon exit

        # Return outside the context manager to avoid accessing the session
        if unhandled_request:
            return jsonify(request_data), 200
        else:
            return jsonify({"message": "No unhandled requests found."}), 404

    def __get_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        request_entry = Request.query.get(request_id)
        if request_entry:
            return jsonify({
                "id": request_entry.id,
                "timestamp": request_entry.timestamp.isoformat(),
                "source_ip": request_entry.source_ip,
                "user_agent": request_entry.user_agent,
                "method": request_entry.method,
                "request_url": request_entry.request_url,
                "request_raw": json.loads(request_entry.request_raw),
                "custom_value": request_entry.custom_value,
                "is_handled": request_entry.is_handled
            }), 200
        else:
            return jsonify({"message": "Request not found"}), 404

    def __update_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        data = request.get_json()
        request_entry = Request.query.get(request_id)
        if request_entry:
            if 'is_handled' in data:
                request_entry.is_handled = data['is_handled']
            db.session.commit()
            return jsonify({"message": "Request updated successfully"}), 200
        else:
            return jsonify({"message": "Request not found"}), 404

    def __delete_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        request_entry = Request.query.get(request_id)
        if request_entry:
            db.session.delete(request_entry)
            db.session.commit()
            return jsonify({"message": "Request deleted successfully"}), 200
        else:
            return jsonify({"message": "Request not found"}), 404

    def run(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

if __name__ == '__main__':
    drumpler = Drumpler()
    drumpler.run()