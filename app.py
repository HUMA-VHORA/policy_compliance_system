from flask import Flask, request, jsonify
import pdfplumber
import os
import re
import numpy as np
import json
import time

from config import Config
from database.db_instance import db
from database.models import Policy, Paragraph

from embeddings.embedding_engine import generate_embedding
from reports.compliance_report import generate_excel_report

from llm.clause_classifier import classify_clause
from llm.explanation_engine import explain_gap
from llm.keyword_engine import extract_keywords
from llm.question_generator import generate_audit_questions


# =====================================================
# APP CONFIGURATION
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def normalize_vector(vector):
    """Normalize embedding vector"""
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def calculate_similarity_list(bank_vec, vendor_embeddings):
    """Calculate cosine similarity scores"""

    similarity_list = []

    for vendor_num, vendor_vec in vendor_embeddings.items():

        score = float(np.dot(bank_vec, vendor_vec))

        similarity_list.append((vendor_num, score))

    similarity_list.sort(key=lambda x: x[1], reverse=True)

    return similarity_list


def get_compliance_status(score):

    if score >= 0.85:
        return "Fully Compliant"

    if score >= 0.65:
        return "Partially Compliant"

    return "Gap"


def generate_explanation(status, bank_text, vendor_text, score):

    if status == "Fully Compliant":
        return "Vendor fully satisfies bank requirement."

    try:

        explanation = explain_gap(
            bank_text,
            vendor_text,
            score
        )

        if not explanation:
            return "Insufficient information for compliance determination."

        return explanation

    except Exception as e:

        print("LLM explanation error:", str(e))

        return "AI explanation unavailable."


def extract_pdf_text(file_path):

    full_text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

    return full_text


def split_into_paragraphs(text):

    paragraphs = re.split(r'\n\s*\n|\n(?=\d+\.)', text)

    return [p.strip() for p in paragraphs if p.strip()]


# =====================================================
# HOME ROUTE
# =====================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Policy Compliance & Gap Analysis System Running"
    })


# =====================================================
# UPLOAD POLICY
# =====================================================

@app.route("/upload_policy", methods=["POST"])
def upload_policy():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    policy_name = request.form.get("policy_name")
    policy_type = request.form.get("policy_type")
    version = request.form.get("version")

    if not policy_name or not policy_type:
        return jsonify({"error": "Policy name and type required"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    full_text = extract_pdf_text(file_path)

    if not full_text.strip():
        return jsonify({"error": "No readable text found"}), 400

    paragraphs = split_into_paragraphs(full_text)

    new_policy = Policy(
        policy_name=policy_name,
        policy_type=policy_type,
        version=version
    )

    db.session.add(new_policy)
    db.session.commit()

    for index_num, para in enumerate(paragraphs, start=1):

        vector = generate_embedding(para)
        vector = normalize_vector(vector).astype(np.float32)

        # Clause classification
        try:
            metadata = classify_clause(para)
        except Exception:
            metadata = {}

        # Keyword extraction
        try:
            keyword_result = extract_keywords(para)

            if isinstance(keyword_result, dict):
                keywords = keyword_result.get("keywords", [])
            else:
                keywords = []

        except Exception:
            keywords = []

        # Audit questions
        try:
            question_result = generate_audit_questions(para)

            if isinstance(question_result, dict):
                questions = question_result.get("questions", [])
            else:
                questions = []

        except Exception:
            questions = []

        paragraph_obj = Paragraph(

            policy_id=new_policy.id,

            paragraph_number=index_num,

            paragraph_text=para,

            embedding=vector.tobytes(),

            metadata=json.dumps(metadata),

            keywords=json.dumps({"keywords": keywords}),

            audit_questions=json.dumps({"questions": questions})

        )

        db.session.add(paragraph_obj)

        # Prevent Gemini rate limit
        time.sleep(1)

    db.session.commit()

    return jsonify({

        "message": "Policy uploaded successfully",

        "policy_id": new_policy.id,

        "total_paragraphs_saved": len(paragraphs)

    })


# =====================================================
# COMPARE POLICIES
# =====================================================

@app.route("/compare_policies", methods=["POST"])
def compare_policies():

    data = request.json

    bank_policy_id = data.get("bank_policy_id")
    vendor_policy_id = data.get("vendor_policy_id")

    if not bank_policy_id or not vendor_policy_id:
        return jsonify({"error": "Both policy IDs required"}), 400

    bank_paragraphs = Paragraph.query.filter_by(
        policy_id=bank_policy_id
    ).all()

    vendor_paragraphs = Paragraph.query.filter_by(
        policy_id=vendor_policy_id
    ).all()

    if not bank_paragraphs or not vendor_paragraphs:
        return jsonify({"error": "Invalid policy IDs"}), 400

    bank_embeddings = {
        p.paragraph_number: np.frombuffer(p.embedding, dtype=np.float32)
        for p in bank_paragraphs
    }

    vendor_embeddings = {
        p.paragraph_number: np.frombuffer(p.embedding, dtype=np.float32)
        for p in vendor_paragraphs
    }

    vendor_para_dict = {p.paragraph_number: p for p in vendor_paragraphs}

    comparison_results = []

    for bank_para in bank_paragraphs:

        bank_num = bank_para.paragraph_number

        bank_vec = bank_embeddings[bank_num]

        similarity_list = calculate_similarity_list(
            bank_vec,
            vendor_embeddings
        )

        best_vendor_num, top_score = similarity_list[0]

        compliance_status = get_compliance_status(top_score)

        vendor_para = vendor_para_dict[best_vendor_num]

        explanation = generate_explanation(
            compliance_status,
            bank_para.paragraph_text,
            vendor_para.paragraph_text,
            top_score
        )

        # Extract keywords
        try:

            keyword_data = json.loads(bank_para.keywords)

            keywords = keyword_data.get("keywords", [])

        except Exception:

            keywords = []

        # Extract audit questions
        try:

            question_data = json.loads(bank_para.audit_questions)

            audit_questions = question_data.get("questions", [])

        except Exception:

            audit_questions = []

        # Top 3 matches
        top_matches = [

            {
                "vendor_para_number": v,
                "similarity_score": round(float(s), 4)
            }

            for v, s in similarity_list[:3]

        ]

        comparison_results.append({

            "bank_section_number": bank_num,

            "matched_vendor_section": best_vendor_num,

            "compliance_status": compliance_status,

            "compliance_percentage": round(top_score * 100, 2),

            "keywords": keywords,

            "audit_questions": audit_questions,

            "top_matches": top_matches,

            "explanation": explanation

        })

    report_file = generate_excel_report(comparison_results)

    return jsonify({

        "comparison_results": comparison_results,

        "report_file": report_file

    })


# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        print("Tables created successfully!")

    app.run(debug=True)