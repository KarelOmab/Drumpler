import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from request import Request
import threading
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from constants import DATABASE_URI, AUTHORIZATION_KEY, NOGGIN_URL, MAMMOTH_WORKERS
import signal

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, nullable=False)
    created_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modified_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    finished_date = Column(DateTime(timezone=True))
    status = Column(String)

    events = relationship("Event", backref="job")

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    message = Column(Text)  # Use Text for potentially longer messages

engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

class Mammoth:
    def __init__(self, process_request_data, noggin_url=NOGGIN_URL, workers=MAMMOTH_WORKERS):
        self.noggin_url = noggin_url
        self.auth_key = AUTHORIZATION_KEY  # Default value if not set
        self.workers = workers if workers is not None else multiprocessing.cpu_count()
        self.stop_signal = threading.Event()  # Use an event to signal workers to stop
        self.user_process_request_data = process_request_data

    def insert_event(self, session, job_id, message):
        start_event = Event(job_id=job_id, message=message)
        session.add(start_event)
        session.commit()
        return True

    def fetch_next_unhandled_request(self, session, noggin_url):
        headers = {"Authorization": f"Bearer {self.auth_key}"}
        try:
            response = requests.get(f"{noggin_url}/request/next-unhandled", headers=headers)
            if response.status_code == 200:
                data = response.json()

                # Create a Job record
                job = Job(request_id=data.get('id'), status='Pending')
                session.add(job)
                session.commit()

                # Return both the Request and Job ID for further processing
                return Request(
                    id=data.get('id'),
                    timestamp=data.get('timestamp'),  
                    source_ip=data.get('source_ip'),
                    user_agent=data.get('user_agent'),
                    method=data.get('method'),
                    request_url=data.get('request_url'),
                    request_raw=data.get('request_raw'),
                    is_handled=data.get('is_handled')
                ), job.id
            else:
                print("Failed to fetch unhandled request:", response.status_code)
                time.sleep(5)
                return None, None
        except requests.exceptions.RequestException as e:
            print("Error fetching unhandled request:", e)
            return None, None

    def process_request_start(self, session, request, job_id):
        if request.request_raw:
            payload = json.loads(request.request_raw)
            thread_id = threading.get_ident()  # Get the current thread's identifier
            
            # Log the start of processing as an event
            start_event = Event(job_id=job_id, message=f'Started processing job:{job_id}, originated from request {request.id}.')
            session.add(start_event)
            session.commit()
            
            return True
        return False
    
    def process_request_complete(self, session, request, job_id):
        if request.request_raw:
            payload = json.loads(request.request_raw)
            thread_id = threading.get_ident()  # Get the current thread's identifier
            
            # Mark job as completed
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = 'Completed'
                job.finished_date = datetime.now(timezone.utc)
                session.add(job)
            
            # Log the completion of processing as an event
            completion_event = Event(job_id=job_id, message=f'Completed processing job:{job_id}, originated from request {request.id}.')
            session.add(completion_event)

            session.commit()
            
            return True
        return False

    def session_factory(self):
        # Factory method to create a new SQLAlchemy session
        return Session()

    def run(self):
        def worker_task(session_factory, noggin_url, auth_key, stop_signal):
            session = session_factory()
            while not stop_signal.is_set():
                request, job_id = self.fetch_next_unhandled_request(session, noggin_url)
                if request and job_id:
                    # Call the user-defined processing function
                    self.process_request_start(session, request, job_id)
                    process = self.user_process_request_data(session, request, job_id)

                    if process:
                        request.mark_as_handled()
                        self.process_request_complete(session, request, job_id)

            session.close()

        # Set up signal handling to catch CTRL+C
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda sig, frame: self.stop_signal.set())

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for _ in range(self.workers):
                executor.submit(worker_task, self.session_factory, self.noggin_url, self.auth_key, self.stop_signal)

        # Restore the original SIGINT handler
        signal.signal(signal.SIGINT, original_sigint_handler)
        print("All workers have been stopped.")

#if __name__ == "__main__":
#    mammoth_app = Mammoth()
#    print("Starting Mammoth application...")
#    mammoth_app.run()