from app import db
import datetime

class Resume(db.Model):
    """Model for the processed resumes"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    candidate_name = db.Column(db.String(100))
    candidate_email = db.Column(db.String(100))
    jd_cv_match_score = db.Column(db.Float, default=0.0)
    batch_years = db.Column(db.Integer, default=0)
    relevant_experience = db.Column(db.Float, default=0.0)
    total_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'

class EmailLog(db.Model):
    """Model for tracking emails sent to candidates"""
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    email_to = db.Column(db.String(100), nullable=False)
    sent_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Sent, Failed, Pending
    
    # Define relationship
    resume = db.relationship('Resume', backref=db.backref('emails', lazy=True))
    
    def __repr__(self):
        return f'<EmailLog {self.email_to} - {self.status}>'
