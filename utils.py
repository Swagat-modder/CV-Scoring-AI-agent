import re
import logging
import csv
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def mask_pii(text):
    """Mask personally identifiable information (PII)"""
    if not text:
        return ""
    
    # For names, keep first character of each word and mask the rest
    words = text.split()
    masked_words = []
    
    for word in words:
        if len(word) > 1:
            masked_word = word[0] + '*' * (len(word) - 1)
        else:
            masked_word = word
        masked_words.append(masked_word)
    
    return ' '.join(masked_words)

def mask_email(email):
    """Mask email address"""
    if not email or '@' not in email:
        return email
    
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]
    
    # Mask username: keep first 2 chars and last char, mask the rest
    if len(username) > 3:
        masked_username = username[:2] + '*' * (len(username) - 3) + username[-1]
    else:
        masked_username = username[:1] + '*' * (len(username) - 1)
    
    # Mask domain: keep the TLD (.com, .org, etc.) but mask the domain name
    domain_parts = domain.split('.')
    domain_name = '.'.join(domain_parts[:-1])
    tld = domain_parts[-1]
    
    if len(domain_name) > 1:
        masked_domain = domain_name[0] + '*' * (len(domain_name) - 1) + '.' + tld
    else:
        masked_domain = domain_name + '.' + tld
    
    return f"{masked_username}@{masked_domain}"

def export_to_csv(resumes, output_file='resume_scores.csv'):
    """Export resume scores to CSV file"""
    try:
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow([
                'ID', 'Masked Name', 'Masked Email', 'JD-CV Match Score',
                'Batch Years', 'Relevant AI Experience', 'Total Score',
                'Upload Date'
            ])
            
            # Write data
            for resume in resumes:
                masked_name = mask_pii(resume.candidate_name)
                masked_email = mask_email(resume.candidate_email)
                
                writer.writerow([
                    resume.id,
                    masked_name,
                    masked_email,
                    f"{resume.jd_cv_match_score:.2f}",
                    resume.batch_years,
                    f"{resume.relevant_experience:.2f}",
                    f"{resume.total_score:.2f}",
                    resume.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        logger.info(f"Successfully exported resume data to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting resume data to CSV: {str(e)}")
        return False

def log_activity(message, log_file='activity.log'):
    """Log activity to file"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {message}\n"
        
        with open(log_file, 'a') as file:
            file.write(log_entry)
        
        return True
    except Exception as e:
        logger.error(f"Error writing to activity log: {str(e)}")
        return False
