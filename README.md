# CV Scoring and Feedback System

An automated system that collects, scores, and provides feedback on resumes through email. This application helps recruiters and HR professionals evaluate candidate resumes efficiently by automating scoring and feedback generation.

## Features

- **Resume Upload**: Upload PDF or DOCX format resumes
- **Automated Scoring**: Score resumes based on education, experience, and skills
- **Feedback Generation**: Generate personalized feedback for candidates
- **Email Notifications**: Send feedback directly to candidates
- **Dashboard**: View and manage all processed resumes
- **Export**: Export results to CSV for further analysis

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy (supports SQLite and PostgreSQL)
- **Document Processing**: PyPDF2, python-docx, NLTK
- **Email Service**: Brevo (formerly Sendinblue)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap

## Installation

### Prerequisites

- Python 3.8+
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cv-scoring-system.git
   cd cv-scoring-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   BREVO_API_KEY=your_brevo_api_key_here
   SENDER_EMAIL=your_verified_email@example.com
   SENDER_NAME=CV Scoring System
   ```

4. Initialize the database:
   ```bash
   python -c "from app import db; db.create_all()"
   ```

5. Run the application:
   ```bash
   python main.py
   ```

6. Access the application at `http://localhost:5000`

## Email Service Configuration

This application uses Brevo (formerly Sendinblue) for sending emails. To configure:

1. Sign up for a free Brevo account at [https://www.brevo.com/](https://www.brevo.com/)
2. Generate an API key in the Brevo dashboard under SMTP & API → API Keys
3. Add the API key to your `.env` file
4. Verify your sender email in Brevo dashboard under Senders & IP → Senders

## Environment Variables

- `BREVO_API_KEY`: Your Brevo API key
- `SENDER_EMAIL`: Email address for sending feedback emails
- `SENDER_NAME`: Name displayed as the sender (default: "CV Scoring System")
- `DATABASE_URL`: Database connection string (default: SQLite)
- `PORT`: Port to run the application (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

## Project Structure

```
cv-scoring-system/
├── app.py               # Flask application setup
├── config.py            # Configuration settings
├── email_service.py     # Email service implementation
├── main.py              # Application entry point
├── models.py            # Database models
├── resume_processor.py  # Resume processing logic
├── scoring_engine.py    # Resume scoring algorithms
├── utils.py             # Utility functions
├── static/              # Static assets (JS, CSS, images)
├── templates/           # HTML templates
├── uploads/             # Directory for uploaded resumes
└── instance/            # Instance-specific data (database)
```

## Deployment

### Local Deployment

For local deployment, follow the installation instructions above.

### Cloud Deployment (Render)

1. Create a GitHub repository with your code
2. Sign up on [Render](https://render.com/)
3. Create a new Web Service and connect to your GitHub repository
4. Set environment variables in the Render dashboard
5. Deploy your application

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.