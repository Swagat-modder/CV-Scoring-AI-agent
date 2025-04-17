import os
import re
import logging
import PyPDF2
from docx import Document
#import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from utils import mask_pii

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {str(e)}")


nlp = None

def extract_text_from_pdf(file_path):
    """Extract text content from a PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
    return text

def extract_text_from_docx(file_path):
    """Extract text content from a DOCX file"""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
    return text

def extract_contact_info(text):
    """Extract name and email from resume text"""
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None
    
    # Extract name - this is more complex and often at the beginning of the resume
    # Using a simplistic approach here - in real life would need more sophisticated NER
    name = None
    
    # Try using spaCy for name extraction if available
    if nlp:
        doc = nlp(text[:1000])  # Process just the first part of the document
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
    
    # If spaCy didn't find a name, try a basic heuristic
    if not name:
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 40 and not re.search(email_pattern, line):
                name = line
                break
    
    return name, email

def extract_education(text):
    """Extract education information and batch years"""
    # Common education keywords
    education_keywords = [
        "education", "university", "college", "bachelor", "master", "phd", 
        "degree", "diploma", "school", "institute", "b.tech", "m.tech", "btech",
        "mtech", "b.e", "m.e", "b.sc", "m.sc", "bsc", "msc"
    ]
    
    # Year pattern
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    years = [int(year) for year in years]
    
    # If we found any years, determine the graduation year (likely the max year)
    batch_years = max(years) if years else 0
    
    # Extract education section using keywords
    education_info = []
    lines = text.split('\n')
    in_education_section = False
    for line in lines:
        line = line.strip().lower()
        
        # Check if this line is an education header
        if any(keyword in line for keyword in education_keywords):
            in_education_section = True
            education_info.append(line)
        # If we're in education section, keep adding lines
        elif in_education_section and line:
            education_info.append(line)
            # Check if we're leaving the education section
            if len(line) > 100 or "experience" in line or "work" in line:
                in_education_section = False
    
    return batch_years, "\n".join(education_info)

def extract_experience(text):
    """Extract work experience information"""
    experience_keywords = [
        "experience", "employment", "work history", "career", "job", 
        "professional experience", "work experience"
    ]
    
    ai_keywords = [
        "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
        "neural network", "nlp", "natural language processing", "computer vision",
        "data science", "tensorflow", "pytorch", "keras", "scikit-learn", "spacy",
        "nltk", "opencv", "predictive modeling", "reinforcement learning"
    ]
    
    # Extract experience years
    experience_pattern = r'(\d+)[+]?\s+years?\s+(?:of\s+)?experience'
    experience_matches = re.findall(experience_pattern, text.lower())
    years_of_experience = sum(int(year) for year in experience_matches) if experience_matches else 0
    
    # Calculate AI-relevant experience
    text_lower = text.lower()
    ai_relevance_score = sum(1 for keyword in ai_keywords if keyword in text_lower)
    ai_experience = min(years_of_experience, ai_relevance_score / 2)  # Rough estimate
    
    # Extract experience section
    experience_info = []
    lines = text.split('\n')
    in_experience_section = False
    for line in lines:
        line = line.strip()
        
        if any(keyword.lower() in line.lower() for keyword in experience_keywords):
            in_experience_section = True
            experience_info.append(line)
        elif in_experience_section and line:
            experience_info.append(line)
            # Check if we're leaving the experience section
            if "education" in line.lower() or "skills" in line.lower():
                in_experience_section = False
    
    return years_of_experience, ai_experience, "\n".join(experience_info)

def extract_skills(text):
    """Extract skills from resume text"""
    # Common technical skills keywords
    skill_keywords = [
        "programming", "languages", "technologies", "frameworks", "tools",
        "libraries", "platforms", "databases", "methodologies", "skills", "technical skills"
    ]
    
    # List of common programming languages, frameworks, and tools
    common_skills = [
        "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "go", "kotlin",
        "react", "angular", "vue", "django", "flask", "spring", "node.js", "express.js",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "sql", "nosql",
        "mongodb", "mysql", "postgresql", "oracle", "firebase", "aws", "azure", "gcp",
        "docker", "kubernetes", "jenkins", "git", "agile", "scrum", "devops", "ci/cd"
    ]
    
    # Extract skills section
    skills = []
    lines = text.split('\n')
    in_skills_section = False
    for line in lines:
        line = line.strip().lower()
        
        if any(keyword in line for keyword in skill_keywords):
            in_skills_section = True
            skills.append(line)
        elif in_skills_section and line:
            skills.append(line)
            # Check if we're leaving the skills section
            if len(line) > 100 or any(section in line for section in ["experience", "education", "projects"]):
                in_skills_section = False
    
    # Find all mentioned skills in the text
    text_lower = text.lower()
    found_skills = [skill for skill in common_skills if skill in text_lower]
    
    return found_skills, "\n".join(skills)

def process_resume(file_path):
    """Process a resume file and extract key information"""
    logger.info(f"Processing resume: {file_path}")
    
    # Determine file type and extract text
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        text = extract_text_from_docx(file_path)
    else:
        logger.error(f"Unsupported file format: {file_extension}")
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    # If text extraction failed
    if not text:
        logger.error(f"Failed to extract text from {file_path}")
        raise ValueError(f"Failed to extract text from {file_path}")
    
    # Extract contact information
    name, email = extract_contact_info(text)
    
    # Extract education and batch years
    batch_years, education_info = extract_education(text)
    
    # Extract experience
    years_experience, ai_experience, experience_info = extract_experience(text)
    
    # Extract skills
    skills, skills_section = extract_skills(text)
    
    # Create resume data dictionary
    resume_data = {
        'text': text,
        'name': name,
        'email': email,
        'masked_name': mask_pii(name) if name else "Anonymous",
        'masked_email': mask_pii(email) if email else "No email provided",
        'batch_years': batch_years,
        'education': education_info,
        'years_experience': years_experience,
        'relevant_experience': ai_experience,
        'skills': skills,
        'skills_section': skills_section,
        'experience_section': experience_info
    }
    
    logger.info(f"Successfully processed resume for {resume_data['masked_name']}")
    return resume_data
