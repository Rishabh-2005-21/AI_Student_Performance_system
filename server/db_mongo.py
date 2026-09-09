"""MongoDB connection, collection access, and default user seeding."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional, List, Dict

import bcrypt

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.environ.get("MONGO_DB_NAME", "ai_student_performance")

_client = None
_db     = None


def get_db():
    """Return the MongoDB database instance (lazy singleton)."""
    global _client, _db
    if _db is None:
        from pymongo import MongoClient
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[DB_NAME]
    return _db


def get_users_col():
    return get_db()["users"]


def get_question_bank_col():
    """Return the question_bank collection."""
    return get_db()["question_bank"]


def get_curriculum_col():
    """Return the curriculum collection."""
    return get_db()["curriculum"]


def get_student_reports_col():
    """Return the student_reports collection."""
    return get_db()["student_reports"]




# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored bcrypt *hashed* value."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

_DEFAULT_FACULTY = [
    {"identifier": "MTR001", "name": "Faculty 1",      "password": "mentor123"},
    {"identifier": "MTR002", "name": "Faculty 2",      "password": "college@123"},
    {"identifier": "ADMIN",  "name": "Administrator",  "password": "admin@123"},
]

_DEFAULT_STUDENTS = [
    {"identifier": "STU001", "name": "Alice Johnson",  "password": "student@123"},
    {"identifier": "STU002", "name": "Bob Sharma",     "password": "student@123"},
]


def seed_default_users() -> None:
    """
    Insert default accounts into MongoDB if they don't already exist.
    Called once on application startup.
    """
    col = get_users_col()

    for u in _DEFAULT_FACULTY:
        if col.find_one({"identifier": u["identifier"], "role": "faculty"}) is None:
            col.insert_one({
                "identifier":    u["identifier"],
                "name":          u["name"],
                "role":          "faculty",
                "password_hash": hash_password(u["password"]),
                "created_at":    datetime.now(timezone.utc),
                "is_active":     True,
            })
            print(f"[MongoDB] Seeded faculty account: {u['identifier']}")

    for u in _DEFAULT_STUDENTS:
        if col.find_one({"identifier": u["identifier"], "role": "student"}) is None:
            col.insert_one({
                "identifier":    u["identifier"],
                "name":          u["name"],
                "role":          "student",
                "password_hash": hash_password(u["password"]),
                "created_at":    datetime.now(timezone.utc),
                "is_active":     True,
            })
            print(f"[MongoDB] Seeded student account: {u['identifier']}")

    # Create a unique index on (identifier, role) to prevent duplicates
    col.create_index([("identifier", 1), ("role", 1)], unique=True, background=True)

    # Create index on question_bank for fast lookups
    try:
        qb_col = get_question_bank_col()
        qb_col.create_index(
            [("mentor_id", 1), ("subject", 1), ("semester", 1)],
            unique=True, background=True
        )
        curr_col = get_curriculum_col()
        curr_col.create_index(
            [("mentor_id", 1), ("key", 1)],
            unique=True, background=True
        )
    except Exception:
        pass



# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_mongo() -> bool:
    """
    Connect to MongoDB and seed default users.
    Returns True if successful, False if MongoDB is unavailable.
    """
    try:
        db = get_db()
        db.command("ping")          # Verify connection
        print(f"[MongoDB] Connected to '{DB_NAME}' at {MONGO_URI}")
        seed_default_users()
        return True
    except Exception as exc:
        print(f"[MongoDB] WARNING: Could not connect — {exc}")
        print("[MongoDB] Falling back to in-memory authentication.")
        return False


def find_user(identifier: str, role: str) -> Optional[dict]:
    """Fetch a user document by identifier and role."""
    try:
        doc = get_users_col().find_one(
            {"identifier": identifier, "role": role, "is_active": True}
        )
        if doc:
            doc["_id"] = str(doc["_id"])  # make JSON-serialisable
        return doc
    except Exception:
        return None


def create_user(identifier: str, name: str, role: str, password: str) -> dict:
    """Insert a new user and return the created document."""
    col = get_users_col()
    if col.find_one({"identifier": identifier, "role": role}):
        raise ValueError(f"Account '{identifier}' already exists for role '{role}'.")
    doc = {
        "identifier":    identifier,
        "name":          name,
        "role":          role,
        "password_hash": hash_password(password),
        "created_at":    datetime.now(timezone.utc),
        "is_active":     True,
    }
    result = col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


# ---------------------------------------------------------------------------
# Question Bank (MongoDB-backed)
# ---------------------------------------------------------------------------

def upsert_question_bank(
    mentor_id: str,
    subject: str,
    semester: str,
    questions: List[Dict],
) -> Dict:
    """
    Save or update the question bank for a mentor/subject/semester.
    Only stores questions with status='approved'.
    """
    col = get_question_bank_col()
    approved = [q for q in questions if q.get("status") == "approved"]
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "mentor_id": mentor_id,
        "subject":   subject.lower(),
        "semester":  str(semester),
        "questions": questions,          # full list (all statuses)
        "total_approved": len(approved),
        "updated_at": now,
    }

    result = col.update_one(
        {"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)},
        {"$set": doc},
        upsert=True,
    )
    return {
        "saved": True,
        "total": len(questions),
        "approved": len(approved),
        "modified": result.modified_count,
        "upserted": result.upserted_id is not None,
    }


def fetch_question_bank(mentor_id: str, subject: str, semester: str) -> Optional[Dict]:
    """Fetch the question bank document for a mentor/subject/semester."""
    try:
        col = get_question_bank_col()
        doc = col.find_one(
            {"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)}
        )
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None


def get_approved_questions(mentor_id: str, subject: str, semester: str) -> List[Dict]:
    """Return only approved questions for student assessment."""
    doc = fetch_question_bank(mentor_id, subject, semester)
    if not doc:
        return []
    return [q for q in doc.get("questions", []) if q.get("status") == "approved"]


def list_question_banks_for_mentor(mentor_id: str) -> List[Dict]:
    """List all question bank entries (tests/assignments) for a mentor with full questions."""
    try:
        col = get_question_bank_col()
        docs = list(col.find(
            {"mentor_id": mentor_id},
            {"_id": 0, "mentor_id": 1, "subject": 1, "semester": 1,
             "questions": 1, "total_approved": 1, "updated_at": 1}
        ))
        for d in docs:
            d["total_questions"] = len(d.get("questions", []))
        return docs
    except Exception:
        return []


def delete_question_bank(mentor_id: str, subject: str, semester: str) -> bool:
    """Delete a saved question bank for a mentor."""
    try:
        col = get_question_bank_col()
        result = col.delete_one({"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)})
        return result.deleted_count > 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Curriculum / Syllabus (MongoDB-backed)
# ---------------------------------------------------------------------------

def upsert_curriculum(
    mentor_id: str,
    subject: str,
    semester: str,
    syllabus_text: str,
    scheme_text: str,
    topics: List[str],
    question_types: List[str],
) -> Dict:
    """
    Save or update a faculty member's uploaded syllabus curriculum in MongoDB.
    """
    col = get_curriculum_col()
    key = f"{subject.lower()}::{str(semester).lower()}"
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "mentor_id":      mentor_id,
        "subject":        subject.lower(),
        "semester":       str(semester).lower(),
        "key":            key,
        "syllabus_text":  syllabus_text,
        "scheme_text":    scheme_text,
        "topics":         topics,
        "question_types": question_types,
        "updated_at":     now,
    }

    result = col.update_one(
        {"mentor_id": mentor_id, "key": key},
        {"$set": doc},
        upsert=True,
    )
    return {
        "saved": True,
        "key": key,
        "mentor_id": mentor_id,
        "modified": result.modified_count,
        "upserted": result.upserted_id is not None,
    }


def fetch_curriculum(mentor_id: str, subject: str, semester: str) -> Optional[Dict]:
    """Fetch curriculum document for a mentor/subject/semester."""
    try:
        col = get_curriculum_col()
        key = f"{subject.lower()}::{str(semester).lower()}"
        doc = col.find_one({"mentor_id": mentor_id, "key": key})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None


def list_curriculum_for_mentor(mentor_id: str) -> List[Dict]:
    """List all curriculum/syllabus documents for a specific faculty member."""
    try:
        col = get_curriculum_col()
        docs = list(col.find(
            {"mentor_id": mentor_id},
            {"_id": 0, "mentor_id": 1, "subject": 1, "semester": 1, "key": 1,
             "topics": 1, "question_types": 1, "updated_at": 1}
        ))
        return docs
    except Exception:
        return []


def delete_curriculum_from_db(mentor_id: str, key: str) -> bool:
    """Delete a curriculum entry for a faculty member from MongoDB."""
    try:
        col = get_curriculum_col()
        result = col.delete_one({"mentor_id": mentor_id, "key": key})
        return result.deleted_count > 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Student Assessment Reports (MongoDB-backed)
# ---------------------------------------------------------------------------

def save_student_report(report_doc: Dict) -> bool:
    """Save or update a completed student assessment report in MongoDB."""
    try:
        col = get_student_reports_col()
        session_id = report_doc.get("session_id")
        if not session_id:
            return False
        now = datetime.now(timezone.utc).isoformat()
        report_doc["saved_at"] = now
        col.update_one({"session_id": session_id}, {"$set": report_doc}, upsert=True)
        return True
    except Exception as exc:
        print(f"[MongoDB] Error saving student report: {exc}")
        return False


def list_student_reports_for_mentor(mentor_id: str) -> List[Dict]:
    """Retrieve all student assessment reports associated with a faculty mentor."""
    try:
        col = get_student_reports_col()
        docs = list(col.find({"mentor_id": mentor_id}, {"_id": 0}))
        return docs
    except Exception:
        return []


