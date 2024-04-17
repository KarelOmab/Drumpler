from .sql_base import db

class SqlRequest(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    source_ip = db.Column(db.String(128))
    user_agent = db.Column(db.String(256))
    method = db.Column(db.String(8))
    request_url = db.Column(db.String(256))
    request_raw = db.Column(db.Text)
    custom_value = db.Column(db.String(256))
    is_handled = db.Column(db.Integer, default=0)
