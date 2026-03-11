# AI Policy Compliance & Gap Analysis System

An AI-powered system that compares **bank policies with vendor policies** and automatically detects **compliance gaps** using **embeddings, similarity analysis, and Gemini AI**.

Project Overview

Organizations often need to ensure that **vendor policies comply with internal regulatory policies**.
This system automates the compliance process by:

* Uploading policy documents (PDF)
* Extracting paragraphs
* Generating embeddings
* Comparing policies using similarity
* Identifying compliance gaps
* Generating AI explanations
* Creating Excel compliance reports

Features

Policy Upload

* Upload policy documents in **PDF format**
* Automatically extracts paragraphs

Clause Classification

AI categorizes clauses into:

* Security
* Data Privacy
* Legal
* Financial
* Compliance
* Operational
* HR
* Other

Keyword Extraction

Important keywords are extracted from each policy clause using AI.

Audit Question Generation

Automatically generates **audit questions** for compliance verification.

Policy Comparison

Compares **bank policy clauses with vendor clauses** using embeddings and cosine similarity.

Compliance Detection

| Score     | Status              |
| --------- | ------------------- |
| ≥ 85%     | Fully Compliant     |
| 65% – 85% | Partially Compliant |
| < 65%     | Gap                 |

AI Gap Explanation

Uses Gemini AI to explain **why a compliance gap exists**.

Excel Compliance Report

Generates a structured Excel report including:

* Bank clause
* Vendor match
* Compliance status
* Similarity score
* Keywords
* Audit questions
* AI explanation

Tech Stack

Backend

* Python
* Flask

Database

* PostgreSQL
* SQLAlchemy

AI / NLP

* Gemini AI
* Text Embeddings
* Cosine Similarity

Libraries

* pdfplumber
* NumPy
* Pandas
* OpenPyXL

Installation

Clone the repository

git clone <https://github.com/HUMA-VHORA/policy_compliance_system.git>

Move into project folder

cd policy_compliance_system

Create virtual environment

python -m venv venv

Activate environment

Windows:

venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Environment Variables

Create a `.env` file and add:

GEMINI_API_KEY=your_api_key_here

Run the Application

Start the Flask server

python app.py

Server will run at:

<http://127.0.0.1:5000>

API Endpoints

Upload Policy

POST /upload_policy

Parameters

* file (PDF)
* policy_name
* policy_type
* version

Compare Policies

POST /compare_policies

Example JSON

{
 "bank_policy_id": 1,
 "vendor_policy_id": 2
}

Example Output

The system generates an **Excel compliance report** containing:

* Compliance score
* Vendor match
* AI explanation
* Keywords
* Audit questions
* Top similarity matches

Future Improvements

* Compliance dashboard
* Risk scoring
* FAISS vector search
* Policy visualization
* Web UI
