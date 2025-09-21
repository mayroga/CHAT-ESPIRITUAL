from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text)
    language = db.Column(db.String(8))
    created_at = db.Column(db.Float, default=time.time)

class Intention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    amen_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.Float, default=time.time)
