from database.db_instance import db
from datetime import datetime

# ==========================
# Policy Model
# ==========================
class Policy(db.Model):
    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(255), nullable=False)
    policy_type = db.Column(db.String(50), nullable=False)
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Paragraphs
    paragraphs = db.relationship("Paragraph", backref="policy", lazy=True)


# ==========================
# Paragraph Model
# ==========================
class Paragraph(db.Model):
    __tablename__ = "paragraphs"

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(
        db.Integer,
        db.ForeignKey("policies.id"),
        nullable=False
    )

    paragraph_number = db.Column(db.Integer)
    paragraph_text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.LargeBinary)

    # 🔥 Fixed AI Columns
    meta_data = db.Column("metadata", db.Text)      # Python attribute renamed to avoid conflict
    keywords = db.Column(db.Text)
    audit_questions = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
