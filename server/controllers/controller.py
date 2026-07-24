"""Controller functions for request/response handling."""

from __future__ import annotations

import io
import os
import random
import datetime
import uuid

import jwt
from flask import jsonify, request
from PyPDF2 import PdfReader

import db_mongo
from services.service import (
    class_dashboard,
    curriculum_options_for_mentor,
    delete_curriculum_entry,
    generate_report,
    get_subjects,
    mentor_dashboard,
    mentor_login,
    next_question,
    start_mentor_session,
    start_session,
    submit_answer,
    upload_curriculum,
    upload_curriculum_from_pdf_text,
)

# Secret key for JWT signing (in production use env var)
JWT_SECRET = os.environ.get("JWT_SECRET", "ai_student_jwt_secret_2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8


def _make_token(user_doc: dict) -> str:
    """Generate a signed JWT for the given user document."""
    payload = {
        "sub":        user_doc["identifier"],
        "name":       user_doc["name"],
        "role":       user_doc["role"],
        "exp":        datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat":        datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def auth_login_controller():
    """
    POST /api/auth/login
    Body: { "identifier": "MTR001", "password": "mentor123", "role": "faculty" }
    Returns: { "token": "...", "role": "faculty", "name": "...", "identifier": "..." }
    """
    data       = request.get_json(force=True, silent=True) or {}
    identifier = data.get("identifier", "").strip()
    password   = data.get("password", "").strip()
    role       = data.get("role", "faculty").strip().lower()

    if not identifier or not password:
        return jsonify({"error": "identifier and password are required"}), 400
    if role not in ("faculty", "student"):
        return jsonify({"error": "role must be 'faculty' or 'student'"}), 400

    # Try MongoDB first
    user = db_mongo.find_user(identifier, role)
    if user and db_mongo.verify_password(password, user["password_hash"]):
        token = _make_token(user)
        return jsonify({
            "token":      token,
            "role":       user["role"],
            "name":       user["name"],
            "identifier": user["identifier"],
        }), 200

    # Fallback: check in-memory MENTORS dict (for resilience when MongoDB is down)
    if role == "faculty":
        try:
            result = mentor_login(identifier, password)
            # Build a synthetic user doc for token generation
            synthetic = {"identifier": identifier, "name": identifier, "role": "faculty"}
            token = _make_token(synthetic)
            return jsonify({
                "token":      token,
                "role":       "faculty",
                "name":       identifier,
                "identifier": identifier,
            }), 200
        except ValueError:
            pass

    return jsonify({"error": "Invalid credentials. Please check your ID and password."}), 401


def auth_register_controller():
    """
    POST /api/auth/register
    Body: { "identifier": "STU003", "name": "Jane Doe", "password": "pass123", "role": "student" }
    """
    data       = request.get_json(force=True, silent=True) or {}
    identifier = data.get("identifier", "").strip()
    name       = data.get("name", "").strip()
    password   = data.get("password", "").strip()
    role       = data.get("role", "student").strip().lower()

    if not identifier or not name or not password:
        return jsonify({"error": "identifier, name, and password are required"}), 400
    if role not in ("faculty", "student"):
        return jsonify({"error": "role must be 'faculty' or 'student'"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        user  = db_mongo.create_user(identifier, name, role, password)
        token = _make_token(user)
        return jsonify({
            "token":      token,
            "role":       user["role"],
            "name":       user["name"],
            "identifier": user["identifier"],
            "message":    "Account created successfully",
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception as exc:
        return jsonify({"error": f"Registration failed: {exc}"}), 500


def subjects_controller():
    return jsonify({"subjects": get_subjects()})


def start_session_controller():
    data = request.get_json(force=True, silent=True) or {}
    student_name = data.get("student_name", "").strip()
    subject = data.get("subject", "").strip()
    if not student_name or not subject:
        return jsonify({"error": "student_name and subject are required"}), 400
    try:
        session = start_session(student_name, subject)
        return jsonify({"session_id": session["session_id"], "subject": subject}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def next_question_controller():
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    try:
        question = next_question(session_id)
        if question is None:
            return jsonify({"message": "Assessment completed"}), 200
        return jsonify({"question": question}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


def submit_answer_controller():
    data = request.get_json(force=True, silent=True) or {}
    required = ["session_id", "question_id", "answer", "confidence"]
    if any(not data.get(k) for k in required):
        return jsonify({"error": f"Required fields: {', '.join(required)}"}), 400
    try:
        result = submit_answer(
            session_id=data["session_id"],
            question_id=data["question_id"],
            answer=str(data["answer"]),
            confidence=str(data["confidence"]),
        )
        return jsonify({"evaluation": result}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def report_controller(session_id: str):
    try:
        report = generate_report(session_id)
        return jsonify(report), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


def class_dashboard_controller():
    return jsonify(class_dashboard()), 200


def mentor_login_controller():
    data = request.get_json(force=True, silent=True) or {}
    mentor_id = str(data.get("mentor_id", "")).strip()
    password = str(data.get("password", "")).strip()
    if not mentor_id or not password:
        return jsonify({"error": "mentor_id and password are required"}), 400
    try:
        return jsonify(mentor_login(mentor_id, password)), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401


def upload_curriculum_controller():
    data = request.get_json(force=True, silent=True) or {}
    required = ["mentor_id", "subject", "semester", "syllabus_text", "scheme_text"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": f"Required fields: {', '.join(required)}"}), 400
    # Parse question_types — accepts list or comma-separated string
    raw_types = data.get("question_types", [])
    if isinstance(raw_types, str):
        question_types = [t.strip() for t in raw_types.split(",") if t.strip()]
    else:
        question_types = list(raw_types)
    try:
        result = upload_curriculum(
            mentor_id=str(data["mentor_id"]).strip(),
            subject=str(data["subject"]).strip(),
            semester=str(data["semester"]).strip(),
            syllabus_text=str(data["syllabus_text"]),
            scheme_text=str(data["scheme_text"]),
            question_types=question_types if question_types else None,
        )
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def start_mentor_session_controller():
    data = request.get_json(force=True, silent=True) or {}
    required = ["mentor_id", "student_name", "enrollment_no", "semester", "subject"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": f"Required fields: {', '.join(required)}"}), 400
    try:
        session = start_mentor_session(
            mentor_id=str(data["mentor_id"]).strip(),
            student_name=str(data["student_name"]).strip(),
            enrollment_no=str(data["enrollment_no"]).strip(),
            semester=str(data["semester"]).strip(),
            subject=str(data["subject"]).strip(),
        )
        return jsonify({"session_id": session["session_id"], "subject": session["subject"]}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def mentor_dashboard_controller():
    mentor_id = request.args.get("mentor_id", "").strip()
    if not mentor_id:
        return jsonify({"error": "mentor_id is required"}), 400
    try:
        return jsonify(mentor_dashboard(mentor_id)), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


# ---------------------------------------------------------------------------
# Multi-format file text extractor
# ---------------------------------------------------------------------------

def _extract_file_text(file_storage) -> str:
    """Extract plain text from PDF, DOCX, DOC, TXT, or PPTX uploads."""
    if not file_storage:
        return ""

    filename = (file_storage.filename or "").lower()
    raw = file_storage.read()
    file_storage.stream.seek(0)

    if not raw:
        return ""

    # --- PDF ---
    if filename.endswith(".pdf") or file_storage.content_type == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(raw))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
            if text:
                return text
        except Exception:
            pass
        # fallback: try decode as plain text
        try:
            return raw.decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""

    # --- DOCX ---
    if filename.endswith(".docx") or filename.endswith(".doc"):
        try:
            # pyrefly: ignore [missing-import]
            from docx import Document
            doc = Document(io.BytesIO(raw))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # Also extract table content
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            return "\n".join(paragraphs).strip()
        except Exception as exc:
            print(f"[DOCX Extract] Error: {exc}")
            # Fallback
            try:
                return raw.decode("utf-8", errors="ignore").strip()
            except Exception:
                return ""

    # --- PPTX ---
    if filename.endswith(".pptx"):
        try:
            from pptx import Presentation
            prs = Presentation(io.BytesIO(raw))
            texts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        texts.append(shape.text.strip())
            return "\n".join(texts).strip()
        except Exception as exc:
            print(f"[PPTX Extract] Error: {exc}")
            return ""

    # --- Plain text (.txt, .md, etc.) ---
    try:
        return raw.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""


# Keep backward-compat alias
_extract_pdf_text = _extract_file_text


def upload_curriculum_pdf_controller():
    mentor_id = request.form.get("mentor_id", "").strip()
    semester = request.form.get("semester", "").strip()
    full_course_file = request.files.get("full_course_pdf")

    if not mentor_id:
        return jsonify({"error": "mentor_id is required"}), 400
    if not semester:
        return jsonify({"error": "semester is required. Please select a semester before uploading."}), 400
    if not full_course_file:
        return jsonify({"error": "full_course_pdf is required"}), 400

    # Parse question_types from form data (comma-separated string or JSON array string)
    raw_types = request.form.get("question_types", "")
    if raw_types:
        question_types = [t.strip() for t in raw_types.split(",") if t.strip()]
    else:
        question_types = None

    try:
        full_course_text = _extract_file_text(full_course_file)
        if not full_course_text or len(full_course_text.strip()) < 50:
            return jsonify({
                "error": (
                    "Could not read text from the uploaded file. "
                    "For PDFs, ensure it is not a scanned image and contains selectable text. "
                    "For Word documents, ensure the file is a valid .docx format."
                )
            }), 400

        result = upload_curriculum_from_pdf_text(
            mentor_id=mentor_id,
            full_course_text=full_course_text,
            semester=semester,
            question_types=question_types,
        )
        result["ingestion_mode"] = "file (text extracted)"
        # Return extracted text for question generation
        result["extracted_text"] = full_course_text[:8000]
        return jsonify(result), 201
    except ValueError as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to process file: {str(exc)}"}), 400


def delete_curriculum_controller():
    data = request.get_json(force=True, silent=True) or {}
    mentor_id = str(data.get("mentor_id", "")).strip()
    key = str(data.get("key", "")).strip()
    if not mentor_id or not key:
        return jsonify({"error": "mentor_id and key are required"}), 400
    try:
        result = delete_curriculum_entry(mentor_id=mentor_id, key=key)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


def curriculum_options_controller():
    mentor_id = request.args.get("mentor_id", "").strip()
    if not mentor_id:
        return jsonify({"error": "mentor_id is required"}), 400
    try:
        return jsonify(curriculum_options_for_mentor(mentor_id)), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


# ---------------------------------------------------------------------------
# Question Generation Controller
# ---------------------------------------------------------------------------

def generate_questions_controller():
    """
    POST /api/mentor/questions/generate
    Body (form-data or JSON):
      - mentor_id
      - subject
      - semester
      - text (extracted document text) OR uploaded file
      - question_types (comma-separated: mcq,short,fill_blank,integer)
      - difficulties (comma-separated: easy,medium,hard)
      - count (number of questions to generate, default 10)
    """
    # Support both JSON and form-data
    if request.content_type and "multipart" in request.content_type:
        mentor_id = request.form.get("mentor_id", "").strip()
        subject   = request.form.get("subject", "subject").strip()
        semester  = request.form.get("semester", "1").strip()
        text      = request.form.get("text", "").strip()
        raw_types = request.form.get("question_types", "mcq,short")
        raw_diffs = request.form.get("difficulties", "easy,medium,hard")
        count     = int(request.form.get("count", 10))
        # If a file is also provided, extract from it
        uploaded_file = request.files.get("file")
        if uploaded_file and not text:
            text = _extract_file_text(uploaded_file)
    else:
        data      = request.get_json(force=True, silent=True) or {}
        mentor_id = str(data.get("mentor_id", "")).strip()
        subject   = str(data.get("subject", "subject")).strip()
        semester  = str(data.get("semester", "1")).strip()
        text      = str(data.get("text", "")).strip()
        raw_types = str(data.get("question_types", "mcq,short"))
        raw_diffs = str(data.get("difficulties", "easy,medium,hard"))
        count     = int(data.get("count", 10))

    if not mentor_id:
        return jsonify({"error": "mentor_id is required"}), 400
    if not text:
        return jsonify({"error": "text (document content) is required"}), 400

    question_types = [t.strip() for t in raw_types.split(",") if t.strip()]
    difficulties   = [d.strip() for d in raw_diffs.split(",") if d.strip()]

    try:
        from ai_engine.question_generator import generate_questions
        result = generate_questions(
            text=text,
            subject=subject,
            question_types=question_types,
            difficulties=difficulties,
            count=count,
        )
        return jsonify(result), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Question generation failed: {str(exc)}"}), 500


# ---------------------------------------------------------------------------
# Question Bank Save / Get / Delete
# ---------------------------------------------------------------------------

def save_question_bank_controller():
    """
    POST /api/mentor/questions/save
    Body: { mentor_id, subject, semester, questions: [...] }
    Saves all questions (approved/rejected/pending) to MongoDB.
    """
    data      = request.get_json(force=True, silent=True) or {}
    mentor_id = str(data.get("mentor_id", "")).strip()
    subject   = str(data.get("subject", "")).strip()
    semester  = str(data.get("semester", "")).strip()
    questions = data.get("questions", [])

    if not mentor_id or not subject or not semester:
        return jsonify({"error": "mentor_id, subject, and semester are required"}), 400
    if not isinstance(questions, list):
        return jsonify({"error": "questions must be a list"}), 400

    try:
        result = db_mongo.upsert_question_bank(mentor_id, subject, semester, questions)
        return jsonify({
            "message": f"Saved {result['approved']} approved questions out of {result['total']} total.",
            **result,
        }), 200
    except Exception as exc:
        return jsonify({"error": f"Save failed: {str(exc)}"}), 500


def get_question_bank_controller():
    """
    GET /api/mentor/questions?mentor_id=&subject=&semester=
    Returns the full question bank for a mentor/subject/semester.
    """
    mentor_id = request.args.get("mentor_id", "").strip()
    subject   = request.args.get("subject", "").strip()
    semester  = request.args.get("semester", "").strip()

    if not mentor_id:
        return jsonify({"error": "mentor_id is required"}), 400

    # If subject/semester not provided, list all banks for mentor
    if not subject or not semester:
        banks = db_mongo.list_question_banks_for_mentor(mentor_id)
        return jsonify({"banks": banks}), 200

    doc = db_mongo.fetch_question_bank(mentor_id, subject, semester)
    if not doc:
        return jsonify({"questions": [], "total_approved": 0}), 200

    return jsonify({
        "subject":        doc.get("subject"),
        "semester":       doc.get("semester"),
        "questions":      doc.get("questions", []),
        "total_approved": doc.get("total_approved", 0),
        "updated_at":     doc.get("updated_at"),
    }), 200


def student_questions_controller():
    """
    GET /api/student/questions?mentor_id=&subject=&semester=&count=10
    Returns a randomly shuffled subset of approved questions for a student.
    """
    mentor_id = request.args.get("mentor_id", "").strip()
    subject   = request.args.get("subject", "").strip()
    semester  = request.args.get("semester", "").strip()
    count     = int(request.args.get("count", 10))

    if not mentor_id or not subject or not semester:
        return jsonify({"error": "mentor_id, subject, and semester are required"}), 400

    approved = db_mongo.get_approved_questions(mentor_id, subject, semester)
    if not approved:
        return jsonify({"error": "No approved questions found for this subject/semester."}), 404

    # Shuffle and pick N
    shuffled = approved.copy()
    random.shuffle(shuffled)
    selected = shuffled[:min(count, len(shuffled))]

    # Strip correct_answer from student-facing response
    for q in selected:
        q.pop("correct_answer", None)
        q.pop("source", None)

    return jsonify({
        "questions": selected,
        "total_available": len(approved),
        "serving": len(selected),
    }), 200