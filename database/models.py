from database.db_instance import db
from datetime import datetime


class Policy(db.Model):
    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(255), nullable=False)
    policy_type = db.Column(db.String(50), nullable=False)
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    paragraphs = db.relationship("Paragraph", backref="policy", lazy=True)


class Paragraph(db.Model):
    __tablename__ = "paragraphs"

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey("policies.id"), nullable=False)
    paragraph_number = db.Column(db.Integer)
    paragraph_text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.LargeBinary)


    created_at = db.Column(db.DateTime, default=datetime.utcnow)
