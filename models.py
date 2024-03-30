from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json

# from app import db
db = SQLAlchemy()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    permissions = db.Column(db.String)

    def __init__(self, name, permissions):
        self.name = name
        self.permissions = json.dumps(permissions)

    def get_permissions(self):
        return json.loads(self.permissions)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    name = db.Column(db.String)
    contact = db.Column(db.String)

    def __init__(self, email, password, role_id, name="Shreya", contact="01552393972"):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id
        self.name = name
        self.contact = contact

    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    code = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, email, code, time):
        self.email = email
        self.code = code
        self.time = time

    def update_code(self, code, time):
        self.code = code
        self.timestamp = time

