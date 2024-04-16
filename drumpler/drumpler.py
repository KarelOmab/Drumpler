# drumpler.py
import os
import json
import sys
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .sql_base import Base  # Import the Base declarative class directly
from .sql_request import SqlRequest
from .sql_job import SqlJob
from .sql_event import SqlEvent

app = Flask(__name__)
db = SQLAlchemy()

class Drumpler:
    def __init__(self):
        self.app = app  # Use the global app instance
        self.__init_env()
        self.__init_config()
        self.__init_db()
        self.__setup_routes()

    def __init_config(self):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SQLALCHEMY_POOL_SIZE'] = 10
        self.app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
        self.app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
        self.app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
        self.AUTHORIZATION_KEY = Config.AUTHORIZATION_KEY
        self.host = Config.DRUMPLER_HOST
        self.port = Config.DRUMPLER_PORT
        self.debug = Config.DRUMPLER_DEBUG

    def __init_db(self):
        db.init_app(self.app)  # Initialize SQLAlchemy with app
        with self.app.app_context():
            Base.metadata.create_all(db.engine)  # Create tables from the same Base used in model definitions

    def __setup_routes(self):
        self.app.add_url_rule('/', view_func=self.hello_world, methods=['GET'])
        self.app.add_url_rule('/request', view_func=self.__process_request, methods=['POST'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__get_request, methods=['GET'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__update_request, methods=['PUT'])
        self.app.add_url_rule('/request/<int:request_id>', view_func=self.__delete_request, methods=['DELETE'])
        self.app.add_url_rule('/jobs/next-pending', view_func=self.__get_next_pending_job, methods=['GET'])
        self.app.add_url_rule('/jobs/<int:job_id>', view_func=self.__update_job, methods=['PUT'])
        self.app.add_url_rule('/jobs/<int:job_id>/update-status', view_func=self.__update_job_status, methods=['PUT'])
        self.app.add_url_rule('/jobs/<int:job_id>/mark-handled', view_func=self.__mark_request_as_handled, methods=['PUT'])
        self.app.add_url_rule('/events', view_func=self.__create_event, methods=['POST'])

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

        new_request = SqlRequest(
            source_ip=request.remote_addr,
            user_agent=request.user_agent.string,
            method=request.method,
            request_url=request.url,
            request_raw=json.dumps(data),
            custom_value=custom_value
        )
        db.session.add(new_request)
        db.session.flush()  # Flush here to assign an ID to new_request without committing the transaction

        if custom_value:
            # do more stuff
            new_job = SqlJob(
                request_id=new_request.id,  # Now new_request.id should be available
                status='Pending'
            )
            db.session.add(new_job)
            db.session.commit()
            return jsonify({"message": "Request processed successfully", "id": new_request.id, "job_id": new_job.id}), 200
        else:
            db.session.commit()
            return jsonify({"message": "Request processed successfully", "id": new_request.id}), 200

    def __get_next_pending_job(self):
        custom_value = request.args.get('custom_value', None)
        try:
            job = db.session.query(SqlJob, SqlRequest)\
                .join(SqlRequest, SqlJob.request_id == SqlRequest.id)\
                .filter(
                    SqlJob.status == 'Pending',
                    SqlRequest.custom_value == custom_value,
                    SqlRequest.is_handled == 0
                ).order_by(SqlJob.created_date).first()

            if job:
                job_data, request_data = job
                # Mark job as being processed
                job_data.is_being_processed = True  
                db.session.commit()  # Commit changes explicitly
                return jsonify({
                    "job_id": job_data.id,
                    "request_id": request_data.id,
                    "source_ip": request_data.source_ip,
                    "user_agent": request_data.user_agent,
                    "method": request_data.method,
                    "request_url": request_data.request_url,
                    "request_raw": request_data.request_raw,
                    "custom_value": request_data.custom_value
                }), 200
            else:
                db.session.rollback()  # Rollback explicitly if nothing found
                return jsonify({"message": "No pending jobs found."}), 404

        except Exception as e:
            db.session.rollback()  # Ensure rollback on exception
            print(f"Exception occurred: {str(e)}")
            return jsonify({"message": "Error occurred."}), 500
        
    def __update_job_status(self, job_id):
        with self.app.app_context():  # Ensure the application context is being used
            job = db.session.query(SqlJob).get(job_id)  # Use db.session.query
            if job:
                job.status = request.json.get('status', job.status)
                db.session.commit()
                return jsonify({"message": "Job status updated successfully"}), 200
            else:
                return jsonify({"message": "Job not found"}), 404

    def __mark_request_as_handled(self, job_id):
        with self.app.app_context():  # Ensure the application context is being used
            job = SqlJob.query.get(job_id)
            if job:
                request = SqlRequest.query.get(job.request_id)
                request.is_handled = 1
                db.session.commit()
                return jsonify({"message": "Request marked as handled"}), 200
            return jsonify({"message": "Job or request not found"}), 404

    def __get_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401
        request_entry = SqlRequest.query.get(request_id)
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
        request_entry = SqlRequest.query.get(request_id)
        if request_entry:
            data = request.get_json()
            request_entry.is_handled = data.get('is_handled', request_entry.is_handled)
            db.session.commit()
            return jsonify({"message": "Request updated successfully"}), 200
        else:
            return jsonify({"message": "Request not found"}), 404

    def __delete_request(self, request_id):
        if not self.__authorize_request():
            return jsonify({"message": "Invalid or missing authorization"}), 401
        request_entry = SqlRequest.query.get(request_id)
        if request_entry:
            db.session.delete(request_entry)
            db.session.commit()
            return jsonify({"message": "Request deleted successfully"}), 200
        else:
            return jsonify({"message": "Request not found"}), 404

    def __create_job(self):
        if not self.__authorize_request():
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.get_json()
        new_job = SqlJob(request_id=data['request_id'], status='Pending')
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'job_id': new_job.id}), 201

    def __update_job(self, job_id):
        if not self.__authorize_request():
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.get_json()
        job = SqlJob.query.get(job_id)
        if job:
            job.status = data.get('status', job.status)
            job.finished_date = data.get('finished_date', job.finished_date)
            db.session.commit()
            return jsonify({"message": "Job updated successfully"}), 200
        else:
            return jsonify({"message": "Job not found"}), 404

    def __create_event(self):
        if not self.__authorize_request():
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.get_json()
        new_event = SqlEvent(job_id=data['job_id'], message=data['message'])
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'event_id': new_event.id}), 201

    def run(self):
        app.run(host=self.host, port=self.port, debug=self.debug)
        #self.app.run()

if __name__ == '__main__':
    drumpler = Drumpler()
    drumpler.run()
