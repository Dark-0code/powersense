"""
Database models for PowerSense
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(255))
    readings = db.relationship('Reading', backref='session', lazy=True, cascade='all, delete-orphan')
    analysis = db.relationship('Analysis', backref='session', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_name': self.session_name,
            'created_at': self.created_at.isoformat(),
            'file_name': self.file_name,
            'reading_count': len(self.readings)
        }

class Reading(db.Model):
    __tablename__ = 'readings'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    analysis_data = db.Column(db.JSON, nullable=False)  # Stores entire analysis as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_data': self.analysis_data,
            'created_at': self.created_at.isoformat()
        }
