import re
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {str(e)}")

# Initialize stopwords
try:
    stop_words = set(stopwords.words('english'))
except:
    logger.warning("Failed to load stopwords, using empty set")
    stop_words = set()

def preprocess_text(text):
    """Clean and preprocess text for analysis"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]
    
    # Rejoin
    return ' '.join(tokens)

def calculate_jd_match(resume_text, job_description):
    """Calculate match score between resume and job description"""
    if not job_description:
        return 0.0
    
    try:
        # Preprocess texts
        processed_resume = preprocess_text(resume_text)
        processed_jd = preprocess_text(job_description)
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform([processed_resume, processed_jd])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        match_score = similarity * 100
        return match_score
    except Exception as e:
        logger.error(f"Error calculating JD match: {str(e)}")
        return 0.0

def score_education(resume_data):
    """Score candidate's education"""
    score = 0
    education_text = resume_data.get('education', '').lower()
    
    # Check for degree levels
    if any(term in education_text for term in ['phd', 'doctorate', 'doctor of philosophy']):
        score += 30
    elif any(term in education_text for term in ['master', 'msc', 'ms', 'ma', 'm.tech', 'mtech', 'mba']):
        score += 25
    elif any(term in education_text for term in ['bachelor', 'bsc', 'bs', 'ba', 'b.tech', 'btech', 'b.e', 'be']):
        score += 20
    
    # Check for prestigious universities/institutions
    prestigious_institutions = [
        'stanford', 'harvard', 'mit', 'caltech', 'princeton', 'oxford', 'cambridge',
        'yale', 'berkeley', 'columbia', 'iit', 'indian institute of technology', 
        'bits', 'nit', 'iisc'
    ]
    
    if any(univ in education_text for univ in prestigious_institutions):
        score += 10
    
    # Check for relevant field
    relevant_fields = [
        'computer science', 'data science', 'artificial intelligence', 'machine learning',
        'information technology', 'statistics', 'mathematics', 'computer engineering',
        'electrical engineering', 'software engineering'
    ]
    
    if any(field in education_text for field in relevant_fields):
        score += 10
    
    # Normalize score to a maximum of 25
    return min(score, 25)

def score_experience(resume_data):
    """Score candidate's work experience"""
    score = 0
    years_experience = resume_data.get('years_experience', 0)
    ai_experience = resume_data.get('relevant_experience', 0)
    experience_text = resume_data.get('experience_section', '').lower()
    
    # Score based on years of experience
    if years_experience >= 10:
        score += 20
    elif years_experience >= 5:
        score += 15
    elif years_experience >= 3:
        score += 10
    elif years_experience >= 1:
        score += 5
    
    # Additional points for AI/ML specific experience
    score += min(ai_experience * 5, 15)
    
    # Check for leadership roles
    leadership_terms = [
        'lead', 'senior', 'manager', 'director', 'head', 'chief', 'principal',
        'supervisor', 'coordinator', 'architect'
    ]
    
    if any(term in experience_text for term in leadership_terms):
        score += 10
    
    # Check for reputable companies
    reputable_companies = [
        'google', 'microsoft', 'amazon', 'apple', 'facebook', 'meta', 'netflix',
        'ibm', 'oracle', 'intel', 'nvidia', 'tesla', 'twitter', 'linkedin',
        'adobe', 'salesforce', 'uber', 'airbnb'
    ]
    
    if any(company in experience_text for company in reputable_companies):
        score += 10
    
    # Normalize score to a maximum of 40
    return min(score, 40)

def score_skills(resume_data):
    """Score candidate's skills"""
    score = 0
    skills = resume_data.get('skills', [])
    
    # Core programming languages
    programming_languages = [
        'python', 'java', 'javascript', 'c++', 'c#', 'scala', 'r', 'julia', 'go', 'ruby'
    ]
    
    # AI/ML specific technologies
    ai_ml_technologies = [
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'matplotlib', 'seaborn', 'nltk', 'spacy', 'opencv', 'transformers', 'huggingface'
    ]
    
    # Data handling technologies
    data_technologies = [
        'sql', 'mysql', 'postgresql', 'mongodb', 'elasticsearch', 'cassandra',
        'hadoop', 'spark', 'kafka', 'airflow', 'luigi'
    ]
    
    # Cloud platforms
    cloud_platforms = [
        'aws', 'azure', 'gcp', 'google cloud', 'ec2', 's3', 'lambda',
        'sagemaker', 'azure ml', 'vertex ai'
    ]
    
    # Count matches in each category
    prog_lang_count = sum(1 for skill in skills if skill in programming_languages)
    ai_ml_count = sum(1 for skill in skills if skill in ai_ml_technologies)
    data_tech_count = sum(1 for skill in skills if skill in data_technologies)
    cloud_count = sum(1 for skill in skills if skill in cloud_platforms)
    
    # Score based on counts
    score += min(prog_lang_count * 2, 8)
    score += min(ai_ml_count * 3, 15)
    score += min(data_tech_count * 2, 8)
    score += min(cloud_count * 1.5, 4)
    
    # Normalize score to a maximum of 35
    return min(score, 35)

def generate_feedback(scores, resume_data):
    """Generate personalized feedback based on scores"""
    total_score = scores['total_score']
    education_score = scores['education_score']
    experience_score = scores['experience_score']
    skills_score = scores['skills_score']
    jd_score = scores['jd_cv_match_score']
    
    feedback = []
    
    # Overall assessment
    if total_score >= 85:
        feedback.append("Your resume is excellent and demonstrates strong qualifications in the field.")
    elif total_score >= 70:
        feedback.append("Your resume shows good qualifications and experience in the field.")
    elif total_score >= 50:
        feedback.append("Your resume shows moderate qualifications. There are several areas where you could strengthen your profile.")
    else:
        feedback.append("Your resume could benefit from significant improvements to better showcase your qualifications.")
    
    # Education feedback
    if education_score >= 20:
        feedback.append("Your educational background is impressive and well-aligned with industry requirements.")
    elif education_score >= 15:
        feedback.append("Your education provides a good foundation for this field.")
    else:
        feedback.append("Consider highlighting more relevant aspects of your education or pursuing additional certifications to strengthen this area.")
    
    # Experience feedback
    if experience_score >= 30:
        feedback.append("Your professional experience is exceptional and demonstrates significant expertise.")
    elif experience_score >= 20:
        feedback.append("You have solid work experience that showcases your capabilities.")
    elif experience_score >= 10:
        feedback.append("Your experience is relevant but could benefit from more emphasis on projects and achievements.")
    else:
        feedback.append("Consider adding more details about your work responsibilities and achievements to strengthen your experience section.")
    
    # Skills feedback
    if skills_score >= 25:
        feedback.append("Your technical skills are comprehensive and highly relevant.")
    elif skills_score >= 15:
        feedback.append("You have a good range of technical skills relevant to the field.")
    else:
        feedback.append("Consider developing and showcasing more technical skills that are in demand in the industry.")
    
    # JD match feedback
    if jd_score >= 75:
        feedback.append("Your resume is well-aligned with the job requirements.")
    elif jd_score >= 50:
        feedback.append("Your resume matches several aspects of the job requirements, but could be better tailored.")
    else:
        feedback.append("Your resume could be more effectively tailored to match the specific job requirements.")
    
    # Specific suggestions based on detected gaps
    skills = resume_data.get('skills', [])
    
    if not any(ai_skill in skills for ai_skill in ['tensorflow', 'pytorch', 'keras']):
        feedback.append("Consider adding experience with popular deep learning frameworks like TensorFlow or PyTorch.")
    
    if resume_data.get('relevant_experience', 0) < 1:
        feedback.append("Highlight any AI/ML projects or experience more prominently in your resume.")
    
    # Join all feedback points
    return "\n\n".join(feedback)

def score_resume(resume_data, job_description=""):
    """Score a resume based on extracted data and job description"""
    try:
        # Get resume text
        resume_text = resume_data.get('text', '')
        
        # Calculate JD match score
        jd_cv_match_score = calculate_jd_match(resume_text, job_description)
        
        # Score different components
        education_score = score_education(resume_data)
        experience_score = score_experience(resume_data)
        skills_score = score_skills(resume_data)
        
        # Calculate total score
        # 25% education + 40% experience + 35% skills
        total_score = education_score + experience_score + skills_score
        
        # Generate scores dictionary
        scores = {
            'education_score': education_score,
            'experience_score': experience_score,
            'skills_score': skills_score,
            'jd_cv_match_score': jd_cv_match_score,
            'total_score': total_score
        }
        
        # Generate feedback
        feedback = generate_feedback(scores, resume_data)
        scores['feedback'] = feedback
        
        logger.info(f"Resume scored: {total_score:.2f}/100, JD match: {jd_cv_match_score:.2f}%")
        return scores
    
    except Exception as e:
        logger.error(f"Error scoring resume: {str(e)}")
        # Return empty scores in case of error
        return {
            'education_score': 0,
            'experience_score': 0,
            'skills_score': 0,
            'jd_cv_match_score': 0,
            'total_score': 0,
            'feedback': "Error occurred during scoring."
        }
