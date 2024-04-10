import os
import sys
from flask import Flask, request, jsonify
from .constants import DRUMPLER_HOST, DRUMPLER_PORT, DRUMPLER_DEBUG, DATABASE_URI, AUTHORIZATION_KEY
import json
from flask_sqlalchemy import SQLAlchemy
from .request import Request as BaseRequest
from sqlalchemy.exc import SQLAlchemyError

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

        db.init_app(self.app)
        with self.app.app_context():
            try:
                db.create_all()  # Attempt to create all tables
            except SQLAlchemyError as e:
                sys.exit(f"Failed to initialize database: {e}")

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

        try:
            data = request.get_json() or {}
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
        except SQLAlchemyError as e:
            return jsonify({"message": f"Failed to process request: {e}"}), 500
    
    def __get_next_unhandled_request(self):
        try:
            with db.session.begin():
                query = db.session.query(Request)\
                    .filter(Request.is_handhandled == 0, 
                            Request.is_being_processed == False)
                custom_value = request.args.get('custom_value', None)
                if custom_value:
                    query = query.filter(Request.custom_value == custom_value)
                unhandled_request = query.order_by(Request.id)\
                    .with_for_update(skip_locked=True).first()

                if unhandled_request:
                    unhandled_request.is_being_processed = True
                    request_data = {
                        "id": unhandled_request.id,
                        # Remainder of your field assignments remain unchanged
                    }
            if unhandled_request:
                return jsonify(request_data), 200
            else:
                return jsonify({"message": "No unhandled requests found."}), 404
        except SQLAlchemyError as e:
            return jsonify({"message": f"Database error: {e}"}), 500

    def __get_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        try:
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
        except SQLAlchemyError as e:
            return jsonify({"message": f"Database error: {e}"}), 500

    def __update_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        try:
            data = request.get_json()
            request_entry = Request.query.get(request_id)
            if request_entry:
                if 'is_handled' in data:
                    request_entry.is_handled = data['is_handled']
                db.session.commit()
                return jsonify({"message": "Request updated successfully"}), 200
            else:
                return jsonify({"message": "Request not found"}), 404
        except SQLAlchemyError as e:
            db.session.rollback()  # Ensure that the session is rolled back in case of error
            return jsonify({"message": f"Failed to update request: {e}"}), 500

    def __delete_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401

        try:
            request_entry = Request.query.get(request_id)
            if request_entry:
                db.session.delete(request_entry)
                db.session.commit()
                return jsonify({"message": "Request deleted successfully"}), 200
            else:
                return jsonify({"message": "Request not found"}), 404
        except SQLAlchemyError as e:
            db.session.rollback()  # It's good practice to roll back the session in case of error
            return jsonify({"message": f"Failed to delete request: {e}"}), 500

    def run(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

if __name__ == '__main__':
    drumpler = Drumpler()
    drumpler.run()