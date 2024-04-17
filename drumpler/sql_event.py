from .sql_base import db

class SqlEvent(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    message = db.Column(db.Text)
