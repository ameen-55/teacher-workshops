from datetime import datetime
from app import db

class Workshop(db.Model):
    """Represents a workshop offered."""
    __tablename__ = 'workshops'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    title_ar = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text, nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    tech_stack = db.Column(db.String(200), nullable=False)
    icon_class = db.Column(db.String(50), nullable=False)
    color_class = db.Column(db.String(50), nullable=False, default='workshop-blue')
    
    registrations = db.relationship('Registration', backref='workshop', lazy=True, cascade="all, delete-orphan")

class Registration(db.Model):
    """Represents an attendee registration for a specific workshop."""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)