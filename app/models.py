from datetime import datetime
from app import db


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gift_preference = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to match
    giving_to = db.relationship('Match', foreign_keys='Match.giver_id', backref='giver', lazy=True)
    receiving_from = db.relationship('Match', foreign_keys='Match.receiver_id', backref='receiver', lazy=True)

    def __repr__(self):
        return f'<Participant {self.name}>'


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    giver_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    email_sent = db.Column(db.Boolean, default=False)
    revealed = db.Column(db.Boolean, default=False)
    thank_you_email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Match: {self.giver_id} -> {self.receiver_id}>'


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Settings {self.key}: {self.value}>'
