import os
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from jinja2 import Template

# Configure logging
logger = logging.getLogger(__name__)

# Brevo configuration
BREVO_API_KEY = os.environ.get('BREVO_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_NAME = os.environ.get('SENDER_NAME', 'CV Scoring System')

def get_email_template():
    """Load email template from file"""
    # Keep the existing function code

def send_feedback_email(recipient_email, recipient_name, score_results):
    """Send feedback email to candidate using Brevo (Sendinblue)"""
    if not BREVO_API_KEY or not SENDER_EMAIL:
        logger.warning("Brevo API key not configured. Email not sent.")
        return False
    
    try:
        # Format feedback for template
        feedback_paragraphs = score_results.get('feedback', '').split('\n\n')
        
        # Prepare template data
        template_data = {
            'name': recipient_name,
            'total_score': f"{score_results.get('total_score', 0):.1f}",
            'jd_match': f"{score_results.get('jd_cv_match_score', 0):.1f}",
            'education_score': f"{score_results.get('education_score', 0):.1f}",
            'experience_score': f"{score_results.get('experience_score', 0):.1f}",
            'skills_score': f"{score_results.get('skills_score', 0):.1f}",
            'feedback_paragraphs': feedback_paragraphs
        }
        
        # Get email template and render
        template = get_email_template()
        html_content = template.render(**template_data)
        
        # Configure Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Create email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient_email, "name": recipient_name}],
            html_content=html_content,
            sender={"name": SENDER_NAME, "email": SENDER_EMAIL},
            subject="Your Resume Evaluation Results"
        )
        
        # Send email
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
            
    except ApiException as e:
        logger.error(f"Brevo API error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {str(e)}")
        return False