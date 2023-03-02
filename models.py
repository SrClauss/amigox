# inicio de models.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone, email, password):
        self.name = name
        self.phone = phone
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
        }

    def to_dict(self):
        return self.serialize()


class Group(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    host = db.Column(db.String(36), db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    allow_break = db.Column(db.Boolean, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    sorted = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, host, created_at, event_date, allow_break, max_value, min_value):
        self.name = name
        self.host = host
        self.created_at = created_at
        self.event_date = event_date
        self.allow_break = allow_break
        self.max_value = max_value
        self.min_value = min_value

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "event_date": self.event_date.strftime("%Y-%m-%d %H:%M:%S"),
            "allow_break": self.allow_break,
            "max_value": self.max_value,
            "min_value": self.min_value,
            "sorted": self.sorted
        }

    def to_dict(self):
        return self.serialize()


class Friend(db.Model):
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), primary_key=True)
    group_id = db.Column(db.String(36), db.ForeignKey(Group.id), primary_key=True)
    sorted_friend_id = db.Column(db.String(36), db.ForeignKey(User.id))
    desired_gift = db.Column(db.String(100))

    def __init__(self, user_id, group_id, sorted_friend_id=None, desired_gift=None):
        self.user_id = user_id
        self.group_id = group_id
        self.sorted_friend_id = sorted_friend_id
        self.desired_gift = desired_gift

    def serialize(self):
        return {
            "user_id": self.user_id,
            "group_id": self.group_id,
            "sorted_friend_id": self.sorted_friend_id,
            "desired_gift": self.desired_gift
        }

    def to_dict(self):
        return self.serialize()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
# fim de models.py
