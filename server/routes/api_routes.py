"""API route registration."""

from __future__ import annotations

from flask import Blueprint

from controllers.controller import (
    auth_login_controller,
    auth_register_controller,
    class_dashboard_controller,
    curriculum_options_controller,
    delete_curriculum_controller,
    delete_question_bank_controller,
    generate_questions_controller,
    get_question_bank_controller,
    mentor_dashboard_controller,
    mentor_login_controller,
    next_question_controller,
    report_controller,
    save_question_bank_controller,
    start_mentor_session_controller,
    start_session_controller,
    student_questions_controller,
    subjects_controller,
    submit_answer_controller,
    upload_curriculum_controller,
    upload_curriculum_pdf_controller,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")



# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@api_bp.post("/auth/login")
def auth_login_route():
    return auth_login_controller()


@api_bp.post("/auth/register")
def auth_register_route():
    return auth_register_controller()


@api_bp.get("/subjects")
def subjects_route():
    return subjects_controller()


@api_bp.post("/session/start")
def start_session_route():
    return start_session_controller()


@api_bp.get("/question/next")
def next_question_route():
    return next_question_controller()


@api_bp.post("/answer/submit")
def submit_answer_route():
    return submit_answer_controller()


@api_bp.get("/report/<session_id>")
def report_route(session_id: str):
    return report_controller(session_id)


@api_bp.get("/dashboard/class")
def class_dashboard_route():
    return class_dashboard_controller()


@api_bp.post("/mentor/login")
def mentor_login_route():
    return mentor_login_controller()


@api_bp.post("/mentor/curriculum")
def upload_curriculum_route():
    return upload_curriculum_controller()


@api_bp.post("/mentor/curriculum/pdf")
def upload_curriculum_pdf_route():
    return upload_curriculum_pdf_controller()


@api_bp.get("/mentor/curriculum/options")
def curriculum_options_route():
    return curriculum_options_controller()


@api_bp.post("/mentor/session/start")
def start_mentor_session_route():
    return start_mentor_session_controller()


@api_bp.post("/student/session/start")
def start_student_session_route():
    return start_mentor_session_controller()


@api_bp.get("/mentor/dashboard")
def mentor_dashboard_route():
    return mentor_dashboard_controller()


@api_bp.delete("/mentor/curriculum")
def delete_curriculum_route():
    return delete_curriculum_controller()


# ---------------------------------------------------------------------------
# Question Generation & Bank routes
# ---------------------------------------------------------------------------

@api_bp.post("/mentor/questions/generate")
def generate_questions_route():
    """Generate AI questions from uploaded document text."""
    return generate_questions_controller()


@api_bp.post("/mentor/questions/save")
def save_question_bank_route():
    """Save approved question bank to MongoDB."""
    return save_question_bank_controller()


@api_bp.get("/mentor/questions")
def get_question_bank_route():
    """Get question bank for a mentor/subject/semester."""
    return get_question_bank_controller()


@api_bp.delete("/mentor/questions")
def delete_question_bank_route():
    """Delete a question bank for a mentor/subject/semester."""
    return delete_question_bank_controller()



# ---------------------------------------------------------------------------
# Student routes
# ---------------------------------------------------------------------------

@api_bp.get("/student/questions")
def student_questions_route():
    """Get shuffled approved questions for a student assessment."""
    return student_questions_controller()