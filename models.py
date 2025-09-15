from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import func

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='college', lazy=True)
    events = db.relationship('Event', backref='college', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'staff', 'student'
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    student_id = db.Column(db.String(50))  # For students
    department = db.Column(db.String(50))
    year_of_study = db.Column(db.Integer)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    registrations = db.relationship('Registration', backref='user', lazy=True)
    check_ins = db.relationship('CheckIn', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)  # 'hackathon', 'workshop', 'tech_talk', 'fest', 'seminar'
    venue = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer)
    registration_deadline = db.Column(db.DateTime)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=False)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    check_ins = db.relationship('CheckIn', backref='event', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_events')
    
    @property
    def registration_count(self):
        return Registration.query.filter_by(event_id=self.id, status='confirmed').count()
    
    @property
    def check_in_count(self):
        return CheckIn.query.filter_by(event_id=self.id).count()
    
    @property
    def is_registration_open(self):
        if not self.registration_deadline:
            return self.start_time > datetime.utcnow()
        return self.registration_deadline > datetime.utcnow()

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'waitlist'
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_registration'),)

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Unique constraint to prevent duplicate check-ins
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_checkin'),)

#New Feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)   # 1–5 scale
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    user = db.relationship('User', backref='feedbacks')
    event = db.relationship('Event', backref='feedbacks')

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_feedback'),)