import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cv_scoring.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the app with the database extension
db.init_app(app)

with app.app_context():
    # Import models
    import models
    db.create_all()

# Import required modules after app initialization
from resume_processor import process_resume
from scoring_engine import score_resume
from email_service import send_feedback_email
from models import Resume, EmailLog

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    """Handle resume uploads"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('resume')
        
        if not files or files[0].filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                try:
                    # Process the resume
                    resume_data = process_resume(file_path)
                    
                    # Score the resume
                    job_description = request.form.get('job_description', '')
                    score_results = score_resume(resume_data, job_description)
                    
                    # Save to database
                    new_resume = Resume(
                        filename=filename,
                        candidate_name=resume_data.get('name', 'Unknown'),
                        candidate_email=resume_data.get('email', 'Unknown'),
                        jd_cv_match_score=score_results.get('jd_cv_match_score', 0),
                        batch_years=resume_data.get('batch_years', 0),
                        relevant_experience=resume_data.get('relevant_experience', 0),
                        total_score=score_results.get('total_score', 0),
                        feedback=score_results.get('feedback', ''),
                        upload_date=datetime.datetime.now()
                    )
                    db.session.add(new_resume)
                    db.session.commit()
                    
                    # Send email if configured and if email is available
                    if resume_data.get('email') and request.form.get('send_email'):
                        email_sent = send_feedback_email(
                            resume_data.get('email'),
                            resume_data.get('name', 'Candidate'),
                            score_results
                        )
                        
                        # Log email status
                        email_log = EmailLog(
                            resume_id=new_resume.id,
                            email_to=resume_data.get('email'),
                            sent_date=datetime.datetime.now(),
                            status='Sent' if email_sent else 'Failed'
                        )
                        db.session.add(email_log)
                        db.session.commit()
                    
                    flash(f'Resume {filename} processed successfully!', 'success')
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
                    flash(f'Error processing {filename}: {str(e)}', 'danger')
            else:
                flash(f'Invalid file type for {file.filename}. Only PDF and DOCX allowed.', 'warning')
        
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    """View processed resumes and scores"""
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    return render_template('dashboard.html', resumes=resumes)

@app.route('/logs')
def view_logs():
    """View email sending logs"""
    email_logs = EmailLog.query.order_by(EmailLog.sent_date.desc()).all()
    return render_template('logs.html', logs=email_logs)

@app.route('/settings')
def settings():
    """Application settings page"""
    return render_template('settings.html')

@app.route('/resend_email/<int:resume_id>')
def resend_email(resume_id):
    """Resend feedback email for a specific resume"""
    resume = Resume.query.get_or_404(resume_id)
    
    if not resume.candidate_email:
        flash('No email address available for this candidate', 'warning')
    else:
        score_results = {
            'jd_cv_match_score': resume.jd_cv_match_score,
            'total_score': resume.total_score,
            'feedback': resume.feedback
        }
        
        email_sent = send_feedback_email(
            resume.candidate_email,
            resume.candidate_name,
            score_results
        )
        
        # Log email status
        email_log = EmailLog(
            resume_id=resume.id,
            email_to=resume.candidate_email,
            sent_date=datetime.datetime.now(),
            status='Sent' if email_sent else 'Failed'
        )
        db.session.add(email_log)
        db.session.commit()
        
        if email_sent:
            flash(f'Email resent successfully to {resume.candidate_email}', 'success')
        else:
            flash(f'Failed to send email to {resume.candidate_email}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
def delete_resume(resume_id):
    """Delete a resume from the system"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Delete associated email logs first (foreign key constraint)
    EmailLog.query.filter_by(resume_id=resume_id).delete()
    
    # Delete the resume
    db.session.delete(resume)
    db.session.commit()
    
    flash('Resume deleted successfully', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
