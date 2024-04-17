from .sql_base import db

class SqlJob(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    modified_date = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    finished_date = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String)
    events = db.relationship("SqlEvent", backref="job", lazy='dynamic')
