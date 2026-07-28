# Zecpath AI

## AI Recruitment System

This project is developed as part of the Zecpath AI Internship. It provides a modular structure for building an AI-powered recruitment platform. The project is organized so that each module is responsible for a specific task in the hiring process.

## Project Layout

The project follows a modular architecture to improve maintainability and scalability.

```
ZECPATH-AI/
│
├── ats_engine/
├── data/
├── interview_ai/
├── parsers/
├── scoring/
├── screening_ai/
├── tests/
├── utils/
├── README.md
├── requirements.txt
└── .gitignore
```

## Folder Description

### data/
Stores datasets, sample resumes, interview data, and other input files used by the AI system.

### parsers/
Contains modules responsible for parsing resumes and extracting candidate information such as skills, education, experience, and certifications.

### ats_engine/
Implements the Applicant Tracking System (ATS) scoring logic by comparing resumes with job descriptions and generating matching scores.

### screening_ai/
Handles the initial AI-based screening process, including voice screening and preliminary candidate evaluation.

### interview_ai/
Contains AI modules responsible for conducting HR and technical interviews and processing candidate responses.

### scoring/
Generates the final candidate score and ranking by combining results from resume screening, interviews, and assessments.

### utils/
Provides reusable utility modules such as logging, configuration, and helper functions shared across the project.

### tests/
Contains test scripts used to verify that different modules of the project are functioning correctly.

## Technologies Used

- Python 3.13
- Virtual Environment (venv)
- Flask
- NumPy
- Pandas
- Requests
- Scikit-learn
- Python-dotenv

## Current Project Status

The project environment has been configured successfully with a modular folder structure, logging system, sample test scripts, and required dependencies. This setup serves as the foundation for implementing AI-powered recruitment modules in subsequent development phases.

## Author

**Nandith Gireesh**