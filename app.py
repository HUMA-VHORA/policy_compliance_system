from flask import Flask, request, jsonify
import pdfplumber
import os
import re
from config import Config
from database.db_instance import db
from database.models import Policy, Paragraph
from embeddings.embedding_engine import generate_embedding, add_to_faiss
from compliance.comparison_engine import compare_embeddings
from reports.compliance_report import generate_excel_report

import numpy as np

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------
# HOME ROUTE
# -----------------------------------
@app.route("/")
def home():
    return {"message": "Policy Compliance & Gap Analysis System Running"}


# -----------------------------------
# UPLOAD POLICY ROUTE
# -----------------------------------
@app.route("/upload_policy", methods=["POST"])
def upload_policy():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    policy_name = request.form.get("policy_name")
    policy_type = request.form.get("policy_type")
    version = request.form.get("version")

    if not policy_name or not policy_type:
        return jsonify({"error": "Policy name and type are required"}), 400

    # Save file locally
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from PDF
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    if not full_text.strip():
        return jsonify({"error": "No readable text found in PDF"}), 400

    # Smart paragraph/section splitting
    paragraphs = re.split(r'\n\s*\n|\n(?=\d+\.)', full_text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # Save policy
    new_policy = Policy(policy_name=policy_name, policy_type=policy_type, version=version)
    db.session.add(new_policy)
    db.session.commit()

    # Save paragraphs with embeddings
    for index_num, para in enumerate(paragraphs, start=1):
        vector = generate_embedding(para)
        add_to_faiss(vector)

        paragraph_obj = Paragraph(
            policy_id=new_policy.id,
            paragraph_number=index_num,
            paragraph_text=para,
            embedding=vector.tobytes()
        )
        db.session.add(paragraph_obj)

    db.session.commit()

    return jsonify({
        "message": "Policy uploaded and stored successfully",
        "policy_id": new_policy.id,
        "policy_type": policy_type,
        "total_paragraphs_saved": len(paragraphs)
    })


# -----------------------------------
# COMPARE POLICIES ROUTE (Updated for cross-section compliance)
# -----------------------------------
@app.route("/compare_policies", methods=["POST"])
def compare_policies():
    bank_policy_id = request.json.get("bank_policy_id")
    vendor_policy_id = request.json.get("vendor_policy_id")

    bank_paragraphs = Paragraph.query.filter_by(policy_id=bank_policy_id).all()
    vendor_paragraphs = Paragraph.query.filter_by(policy_id=vendor_policy_id).all()

    if not bank_paragraphs or not vendor_paragraphs:
        return jsonify({"error": "Invalid policy IDs"}), 400

    # Convert embeddings to numpy arrays
    bank_embeddings = {p.paragraph_number: np.frombuffer(p.embedding, dtype=np.float32) for p in bank_paragraphs}
    vendor_embeddings = {p.paragraph_number: np.frombuffer(p.embedding, dtype=np.float32) for p in vendor_paragraphs}

    comparison_results = []

    for bank_num, bank_vec in bank_embeddings.items():
        similarity_list = []

        # Compare with all vendor paragraphs
        for vendor_num, vendor_vec in vendor_embeddings.items():
            score = np.dot(bank_vec, vendor_vec) / (np.linalg.norm(bank_vec) * np.linalg.norm(vendor_vec))
            similarity_list.append((vendor_num, score))

        # Sort descending by similarity
        similarity_list.sort(key=lambda x: x[1], reverse=True)

        # Determine compliance based on highest similarity
        top_score = similarity_list[0][1]
        if top_score >= 0.85:
            compliance_status = "Fully Compliant"
        elif top_score >= 0.65:
            compliance_status = "Partially Compliant"
        else:
            compliance_status = "Gap"

        # Prepare top 3 matches
        top_matches = [
            {"vendor_para_number": vendor_num, "similarity_score": float(score)}
            for vendor_num, score in similarity_list[:3]
        ]

        comparison_results.append({
            "bank_section_number": bank_num,
            "compliance_status": compliance_status,
            "top_matches": top_matches
        })

    # Optionally generate Excel report
    report_file = generate_excel_report(comparison_results)

    return jsonify({
        "comparison_results": comparison_results,
        "report_file": report_file
    })


# -----------------------------------
# RUN APPLICATION
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)
