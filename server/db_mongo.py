"""MongoDB connection, collection access, default user seeding, and in-memory fallback stores."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional, List, Dict

import bcrypt

import json

# ---------------------------------------------------------------------------
# Persistent Disk Storage File (ensures data survives restarts & logouts)
# ---------------------------------------------------------------------------
STORAGE_FILE = os.path.join(os.path.dirname(__file__), "data_storage.json")

_IN_MEMORY_USERS: Dict[str, Dict] = {}
_IN_MEMORY_QUESTION_BANKS: Dict[str, Dict] = {}
_IN_MEMORY_CURRICULUM: Dict[str, Dict] = {}
_IN_MEMORY_STUDENT_REPORTS: Dict[str, Dict] = {}


def _save_storage_file():
    """Flush in-memory stores to disk so data persists permanently across restarts and logouts."""
    try:
        data = {
            "users": {f"{k[0]}::{k[1]}": v for k, v in _IN_MEMORY_USERS.items()},
            "question_banks": _IN_MEMORY_QUESTION_BANKS,
            "curriculum": _IN_MEMORY_CURRICULUM,
            "student_reports": _IN_MEMORY_STUDENT_REPORTS,
        }
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as exc:
        print(f"[Storage] Notice saving storage file: {exc}")


def _load_storage_file():
    """Load persistent storage file into memory on startup."""
    if not os.path.exists(STORAGE_FILE):
        return
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            users_data = data.get("users", {})
            for key_str, v in users_data.items():
                parts = key_str.split("::")
                if len(parts) == 2:
                    _IN_MEMORY_USERS[(parts[0], parts[1])] = v
            _IN_MEMORY_QUESTION_BANKS.update(data.get("question_banks", {}))
            _IN_MEMORY_CURRICULUM.update(data.get("curriculum", {}))
            _IN_MEMORY_STUDENT_REPORTS.update(data.get("student_reports", {}))
            print(f"[Storage] Loaded persistent data from disk: {len(_IN_MEMORY_CURRICULUM)} curriculum items, {len(_IN_MEMORY_QUESTION_BANKS)} question banks.")
    except Exception as exc:
        print(f"[Storage] Notice loading storage file: {exc}")


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
    Insert default accounts into MongoDB or in-memory fallback.
    """
    # Seed in-memory store
    for u in _DEFAULT_FACULTY:
        _IN_MEMORY_USERS[(u["identifier"], "faculty")] = {
            "identifier": u["identifier"],
            "name": u["name"],
            "role": "faculty",
            "password_hash": hash_password(u["password"]),
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }
    for u in _DEFAULT_STUDENTS:
        _IN_MEMORY_USERS[(u["identifier"], "student")] = {
            "identifier": u["identifier"],
            "name": u["name"],
            "role": "student",
            "password_hash": hash_password(u["password"]),
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }

    # Seed MongoDB if accessible
    try:
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

        col.create_index([("identifier", 1), ("role", 1)], unique=True, background=True)

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
    except Exception as exc:
        print(f"[MongoDB] Notice during seeding (in-memory active): {exc}")
    finally:
        _save_storage_file()



# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_mongo() -> bool:
    """
    Connect to MongoDB and seed default users.
    Returns True if successful, False if MongoDB is unavailable.
    """
    _load_storage_file()
    seed_default_users()
    try:
        db = get_db()
        db.command("ping")          # Verify connection
        print(f"[MongoDB] Connected to '{DB_NAME}' at {MONGO_URI}")
        return True
    except Exception as exc:
        print(f"[MongoDB] WARNING: Could not connect — {exc}")
        print("[MongoDB] Falling back to in-memory storage.")
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
        pass
    # Fallback to in-memory store
    return _IN_MEMORY_USERS.get((identifier, role))


def create_user(identifier: str, name: str, role: str, password: str) -> dict:
    """Insert a new user and return the created document."""
    existing = find_user(identifier, role)
    if existing:
        raise ValueError(f"Account '{identifier}' already exists for role '{role}'.")

    doc = {
        "identifier":    identifier,
        "name":          name,
        "role":          role,
        "password_hash": hash_password(password),
        "created_at":    datetime.now(timezone.utc),
        "is_active":     True,
    }
    _IN_MEMORY_USERS[(identifier, role)] = doc

    try:
        col = get_users_col()
        result = col.insert_one(doc.copy())
        doc["_id"] = str(result.inserted_id)
    except Exception as exc:
        print(f"[MongoDB] Notice during create_user: {exc}")

    _save_storage_file()
    return doc



# ---------------------------------------------------------------------------
# Question Bank (MongoDB-backed with in-memory fallback)
# ---------------------------------------------------------------------------

def upsert_question_bank(
    mentor_id: str,
    subject: str,
    semester: str,
    questions: List[Dict],
) -> Dict:
    """
    Save or update the question bank for a mentor/subject/semester.
    """
    approved = [q for q in questions if q.get("status") == "approved"]
    now = datetime.now(timezone.utc).isoformat()
    key = f"{mentor_id}::{subject.lower()}::{str(semester)}"

    doc = {
        "mentor_id": mentor_id,
        "subject":   subject.lower(),
        "semester":  str(semester),
        "questions": questions,          # full list (all statuses)
        "total_approved": len(approved),
        "updated_at": now,
    }

    # Save to in-memory fallback cache
    _IN_MEMORY_QUESTION_BANKS[key] = doc

    modified = 1
    upserted = True

    try:
        col = get_question_bank_col()
        result = col.update_one(
            {"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)},
            {"$set": doc},
            upsert=True,
        )
        modified = result.modified_count
        upserted = result.upserted_id is not None
    except Exception as exc:
        print(f"[MongoDB] Notice during upsert_question_bank (saved in-memory): {exc}")

    _save_storage_file()
    return {
        "saved": True,
        "total": len(questions),
        "approved": len(approved),
        "modified": modified,
        "upserted": upserted,
    }


def fetch_question_bank(mentor_id: str, subject: str, semester: str) -> Optional[Dict]:
    """Fetch the question bank document for a mentor/subject/semester."""
    key = f"{mentor_id}::{subject.lower()}::{str(semester)}"
    try:
        col = get_question_bank_col()
        doc = col.find_one(
            {"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)}
        )
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
    except Exception:
        pass

    return _IN_MEMORY_QUESTION_BANKS.get(key)


def get_approved_questions(mentor_id: str, subject: str, semester: str) -> List[Dict]:
    """Return only approved questions for student assessment."""
    doc = fetch_question_bank(mentor_id, subject, semester)
    if not doc:
        return []
    return [q for q in doc.get("questions", []) if q.get("status") == "approved"]


def list_question_banks_for_mentor(mentor_id: str) -> List[Dict]:
    """List all question bank entries (tests/assignments) for a mentor with full questions."""
    results_map: Dict[str, Dict] = {}

    # 1. Read from in-memory store
    prefix = f"{mentor_id}::"
    for k, doc in _IN_MEMORY_QUESTION_BANKS.items():
        if k.startswith(prefix):
            sub_key = f"{doc['subject']}::{doc['semester']}"
            results_map[sub_key] = {
                "mentor_id": doc["mentor_id"],
                "subject": doc["subject"],
                "semester": doc["semester"],
                "questions": doc.get("questions", []),
                "total_approved": doc.get("total_approved", 0),
                "total_questions": len(doc.get("questions", [])),
                "updated_at": doc.get("updated_at"),
            }

    # 2. Merge from MongoDB if available
    try:
        col = get_question_bank_col()
        docs = list(col.find(
            {"mentor_id": mentor_id},
            {"_id": 0, "mentor_id": 1, "subject": 1, "semester": 1,
             "questions": 1, "total_approved": 1, "updated_at": 1}
        ))
        for d in docs:
            d["total_questions"] = len(d.get("questions", []))
            sub_key = f"{d['subject']}::{d['semester']}"
            results_map[sub_key] = d
    except Exception as exc:
        print(f"[MongoDB] Notice during list_question_banks_for_mentor: {exc}")

    return list(results_map.values())


def delete_question_bank(mentor_id: str, subject: str, semester: str) -> bool:
    """Delete a saved question bank for a mentor."""
    key = f"{mentor_id}::{subject.lower()}::{str(semester)}"
    existed = key in _IN_MEMORY_QUESTION_BANKS
    if existed:
        del _IN_MEMORY_QUESTION_BANKS[key]

    db_deleted = False
    try:
        col = get_question_bank_col()
        result = col.delete_one({"mentor_id": mentor_id, "subject": subject.lower(), "semester": str(semester)})
        db_deleted = result.deleted_count > 0
    except Exception:
        pass

    _save_storage_file()
    return existed or db_deleted


# ---------------------------------------------------------------------------
# Curriculum / Syllabus (MongoDB-backed with in-memory fallback)
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
    Save or update a faculty member's uploaded syllabus curriculum.
    """
    key = f"{subject.lower()}::{str(semester).lower()}"
    now = datetime.now(timezone.utc).isoformat()
    store_key = f"{mentor_id}::{key}"

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

    _IN_MEMORY_CURRICULUM[store_key] = doc

    modified = 1
    upserted = True
    try:
        col = get_curriculum_col()
        result = col.update_one(
            {"mentor_id": mentor_id, "key": key},
            {"$set": doc},
            upsert=True,
        )
        modified = result.modified_count
        upserted = result.upserted_id is not None
    except Exception as exc:
        print(f"[MongoDB] Notice during upsert_curriculum (saved in-memory): {exc}")

    _save_storage_file()
    return {
        "saved": True,
        "key": key,
        "mentor_id": mentor_id,
        "modified": modified,
        "upserted": upserted,
    }


def fetch_curriculum(mentor_id: str, subject: str, semester: str) -> Optional[Dict]:
    """Fetch curriculum document for a mentor/subject/semester."""
    key = f"{subject.lower()}::{str(semester).lower()}"
    store_key = f"{mentor_id}::{key}"
    try:
        col = get_curriculum_col()
        doc = col.find_one({"mentor_id": mentor_id, "key": key})
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
    except Exception:
        pass

    return _IN_MEMORY_CURRICULUM.get(store_key)


def list_curriculum_for_mentor(mentor_id: str) -> List[Dict]:
    """List all curriculum/syllabus documents for a specific faculty member."""
    results_map: Dict[str, Dict] = {}

    prefix = f"{mentor_id}::"
    for k, doc in _IN_MEMORY_CURRICULUM.items():
        if k.startswith(prefix):
            results_map[doc["key"]] = {
                "mentor_id": doc["mentor_id"],
                "subject": doc["subject"],
                "semester": doc["semester"],
                "key": doc["key"],
                "topics": doc.get("topics", []),
                "question_types": doc.get("question_types", []),
                "updated_at": doc.get("updated_at"),
            }

    try:
        col = get_curriculum_col()
        docs = list(col.find(
            {"mentor_id": mentor_id},
            {"_id": 0, "mentor_id": 1, "subject": 1, "semester": 1, "key": 1,
             "topics": 1, "question_types": 1, "updated_at": 1}
        ))
        for d in docs:
            results_map[d["key"]] = d
    except Exception as exc:
        print(f"[MongoDB] Notice during list_curriculum_for_mentor: {exc}")

    return list(results_map.values())


def delete_curriculum_from_db(mentor_id: str, key: str) -> bool:
    """Delete a curriculum entry for a faculty member."""
    store_key = f"{mentor_id}::{key}"
    existed = store_key in _IN_MEMORY_CURRICULUM
    if existed:
        del _IN_MEMORY_CURRICULUM[store_key]

    db_deleted = False
    try:
        col = get_curriculum_col()
        result = col.delete_one({"mentor_id": mentor_id, "key": key})
        db_deleted = result.deleted_count > 0
    except Exception:
        pass

    _save_storage_file()
    return existed or db_deleted


# ---------------------------------------------------------------------------
# Student Assessment Reports (MongoDB-backed with in-memory fallback)
# ---------------------------------------------------------------------------

def save_student_report(report_doc: Dict) -> bool:
    """Save or update a completed student assessment report."""
    session_id = report_doc.get("session_id")
    if not session_id:
        return False

    now = datetime.now(timezone.utc).isoformat()
    report_doc["saved_at"] = now
    _IN_MEMORY_STUDENT_REPORTS[session_id] = report_doc

    try:
        col = get_student_reports_col()
        col.update_one({"session_id": session_id}, {"$set": report_doc}, upsert=True)
        return True
    except Exception as exc:
        print(f"[MongoDB] Notice saving student report (saved in-memory): {exc}")

    _save_storage_file()
    return True


def list_student_reports_for_mentor(mentor_id: str) -> List[Dict]:
    """Retrieve all student assessment reports associated with a faculty mentor."""
    results_map: Dict[str, Dict] = {}

    for sid, doc in _IN_MEMORY_STUDENT_REPORTS.items():
        if doc.get("mentor_id") == mentor_id:
            results_map[sid] = doc

    try:
        col = get_student_reports_col()
        docs = list(col.find({"mentor_id": mentor_id}, {"_id": 0}))
        for d in docs:
            if d.get("session_id"):
                results_map[d["session_id"]] = d
    except Exception as exc:
        print(f"[MongoDB] Notice listing student reports: {exc}")

    return list(results_map.values())
