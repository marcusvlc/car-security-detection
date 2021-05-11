'''
Relational entity models for the app
'''
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import DateTime
import datetime
from app.ext import db
from werkzeug.security import generate_password_hash, check_password_hash
import jsonpickle
import datetime
import cv2
import numpy as np

class User(db.Model):
    id = db.Column(db.Integer, auto_increment=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    streams = db.relationship("Stream", backref="user", lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def to_json(self):
        return {"name": self.name, "email": self.email, "id": self.id}

    def __repr__(self):
        return '<User %r>' % self.email

class Stream(db.Model):
    id = db.Column(db.Integer, auto_increment=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    stream_url = db.Column(db.String(255), nullable=True)
    stream_type = db.Column(db.String(255), nullable=False)
    stream_file = db.Column(db.LargeBinary, nullable=True)
    plates = db.relationship("Plate", backref="stream", lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    def __init__(self, name, stream_url, stream_type, stream_file, user_id):
        self.name = name
        self.stream_url = stream_url
        self.stream_type = stream_type
        self.stream_file = stream_file
        self.user_id = user_id
    
    def get_decoded_file(self):
        return cv2.imdecode(np.frombuffer(self.stream_file, np.uint8), -1)

    def to_json(self):
        # decoded_file = self.stream_file.decode("utf-8", "ignore") if self.stream_file != None else self.stream_file
        return {"id": self.id, "name": self.name, "stream_url": self.stream_url, "stream_type": self.stream_type, "owner": self.user_id}

    def __repr__(self):
        return '<Stream %r>' % self.id

class Plate(db.Model):
    id = db.Column(db.Integer, auto_increment=True, primary_key=True)
    plate_number = db.Column(db.String(255), nullable=False)
    detected_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False, index=True)

    def to_json(self):
        return {"id": self.id, "plate_number": self.plate_number, "stream_id": self.stream_id}

    def __init__(self, plate_number, stream_id):
        self.plate_number = plate_number
        self.stream_id = stream_id

    def __repr__(self):
        return '<Plate %r with date %r with stream_id %r>' % (self.plate_number, self.detected_date, self.stream_id)