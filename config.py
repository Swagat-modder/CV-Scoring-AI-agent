import os
import logging

# Application configuration
APP_NAME = "CV Scoring System"
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))

# File upload settings
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///cv_scoring.db')

# Email settings (Brevo - formerly Sendinblue)
BREVO_API_KEY = os.environ.get('BREVO_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_NAME = os.environ.get('SENDER_NAME', 'CV Scoring System')

# Scoring weights (out of 100)
SCORE_WEIGHTS = {
    'education': 25,
    'experience': 40,
    'skills': 35
}

# Logging configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
