"""Assessment business logic and in-memory session management."""

from __future__ import annotations

import random
import re
import uuid
from collections import Counter, defaultdict
from typing import Dict, List, Optional

from ai_engine.evaluator import (
    calculate_weighted_score,
    confidence_bucket,
    evaluate_fill_blank,
    evaluate_integer,
    evaluate_mcq,
    evaluate_subjective,
)
from data.question_bank import QUESTION_BANK


DIFFICULTY_ORDER = ["easy", "medium", "hard"]

SESSIONS: Dict[str, Dict] = {}
CLASS_SESSIONS: List[str] = []
MENTORS: Dict[str, str] = {"MTR001": "mentor123", "MTR002": "college@123"}
MENTOR_CURRICULUM: Dict[str, Dict] = {}


def get_subjects() -> List[Dict[str, str]]:
    return [{"id": key, "name": key.replace("_", " ").title()} for key in QUESTION_BANK]


def start_session(student_name: str, subject: str) -> Dict:
    if subject not in QUESTION_BANK:
        raise ValueError("Invalid subject")
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "session_id": session_id,
        "student_name": student_name,
        "subject": subject,
        "current_difficulty": "medium",
        "asked_questions": [],
        "responses": [],
        "completed": False,
    }
    CLASS_SESSIONS.append(session_id)
    return SESSIONS[session_id]


def mentor_login(mentor_id: str, password: str) -> Dict[str, str]:
    if MENTORS.get(mentor_id) != password:
        raise ValueError("Invalid mentor ID or password")
    return {"mentor_id": mentor_id, "message": "Login successful"}


def _extract_topics_from_text(syllabus_text: str, scheme_text: str) -> List[str]:
    combined = f"{syllabus_text}\n{scheme_text}"
    raw_parts = re.split(r"[\n,;|]+", combined)
    topics = []
    for part in raw_parts:
        cleaned = re.sub(r"\s+", " ", part).strip(" -:\t")
        if len(cleaned) >= 3:
            topics.append(cleaned.lower())
    # keep order while removing duplicates
    unique_topics = list(dict.fromkeys(topics))
    return unique_topics[:12]


def upload_curriculum(
    mentor_id: str,
    subject: str,
    semester: str,
    syllabus_text: str,
    scheme_text: str,
    question_types: Optional[List[str]] = None,
) -> Dict[str, str]:
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")
    if not subject or not semester:
        raise ValueError("subject and semester are required")
    if not syllabus_text.strip() or not scheme_text.strip():
        raise ValueError("syllabus_text and scheme_text are required")

    topics = _extract_topics_from_text(syllabus_text, scheme_text)
    if not topics:
        raise ValueError("Could not extract topics from syllabus/scheme")

    # Default to MCQ + short if no types selected
    valid_types = {"mcq", "short", "fill_blank", "integer"}
    if not question_types:
        question_types = ["mcq", "short"]
    else:
        question_types = [t for t in question_types if t in valid_types]
        if not question_types:
            question_types = ["mcq", "short"]

    mentor_data = MENTOR_CURRICULUM.setdefault(mentor_id, {})
    mentor_data[f"{subject.lower()}::{semester.lower()}"] = {
        "subject": subject.lower(),
        "semester": semester.lower(),
        "syllabus_text": syllabus_text,
        "scheme_text": scheme_text,
        "topics": topics,
        "question_types": question_types,
    }
    return {
        "message": "Curriculum uploaded successfully",
        "mentor_id": mentor_id,
        "subject": subject.lower(),
        "semester": semester.lower(),
        "topics_count": str(len(topics)),
        "question_types": question_types,
    }


def _is_clean_english_topic(text: str) -> bool:
    """Return True only if the text looks like a proper English academic topic."""
    if len(text) < 4 or len(text) > 80:
        return False
    # Must contain at least one ASCII letter
    if not any(c.isalpha() and ord(c) < 128 for c in text):
        return False
    # Reject if more than 30% of chars are non-ASCII (catches Hindi/garbled text)
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii / len(text) > 0.3:
        return False
    # Reject purely numeric strings
    if re.fullmatch(r"[\d\s\.\-]+", text):
        return False
    # Reject very short words that are likely codes or fragments
    words = text.split()
    if len(words) == 1 and len(text) < 5:
        return False
    return True


def _extract_clean_topics_from_text(full_text: str, max_topics: int = 12) -> List[str]:
    """Extract real, clean English academic topics from PDF text."""
    raw_parts = re.split(r"[\n,;|•\t]+", full_text)
    seen: Dict[str, bool] = {}
    topics: List[str] = []
    for part in raw_parts:
        cleaned = re.sub(r"\s+", " ", part).strip(" -:\t.()[]{}0123456789")
        # Title-case normalisation for single words; preserve mixed for phrases
        if _is_clean_english_topic(cleaned):
            key = cleaned.lower()
            if key not in seen:
                seen[key] = True
                topics.append(cleaned)
        if len(topics) >= max_topics:
            break
    return topics


def _parse_syllabus_for_semester(
    full_text: str,
    semester: str,
) -> List[Dict]:
    """
    Extract subjects and topics for a specific semester from the uploaded PDF text.
    Strictly uses content from the PDF — no mock/hardcoded fallback data.
    Raises ValueError if the PDF yields no usable academic content.
    """
    # Split into lines for structural analysis
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    subjects: List[Dict] = []
    current_subject: Optional[str] = None
    current_lines: List[str] = []

    def _is_valid_subject_heading(line: str) -> bool:
        """
        Strict gate: a line qualifies as a subject heading only if it looks like
        a proper English academic subject name.

        Rules:
        - Must pass the clean-English topic filter (no garbled chars, no pure digits)
        - Must start with a capital letter
        - Must be ≤ 8 words (headings are short)
        - If single word: must be ≥ 6 chars (rejects 'Oos', 'Crt', 'Fal', 'Qlgc')
        - If multi-word (≥ 2 words): ALL tokens must be at least 2 chars and
          contain only letters (rejects 'C E', 'C5x', 'Xdx7')
        - No digits inside words (rejects 'Xqj8', 'C5x', 'Xdx7')
        """
        if not _is_clean_english_topic(line):
            return False
        if not line[0].isupper():
            return False

        words = line.split()
        if len(words) > 8:
            return False

        # Reject if ANY word contains a digit
        if any(any(c.isdigit() for c in w) for w in words):
            return False

        if len(words) == 1:
            # Single-word heading: must be a real word ≥ 6 chars
            # Rejects: 'Oos' (3), 'Crt' (3), 'Fal' (3), 'Qlgc' (4), 'Jikg' (4)
            # Allows: 'Algorithms' (10), 'Physics' (7), 'Chemistry' (9)
            return len(line) >= 6 and line.isalpha()

        # Multi-word: every token must be purely alphabetic and ≥ 2 chars
        # Rejects: 'C E' (C is 1 char), 'C5x ...'
        return all(len(w) >= 2 and w.isalpha() for w in words)

    def _flush_subject() -> None:
        nonlocal current_subject, current_lines
        if current_subject:
            topics = _extract_clean_topics_from_text("\n".join(current_lines), max_topics=10)
            # Only save if we actually found real topics from the PDF text
            if topics:
                subjects.append({"subject": current_subject, "topics": topics})
            # If no topics found under this heading, skip — don't inject fake data

    for line in lines:
        if _is_valid_subject_heading(line):
            _flush_subject()
            current_subject = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    _flush_subject()  # flush final subject block

    # If heading-based parsing yielded nothing, try treating the whole document
    # as a single flat topic list (e.g., a bullet-point syllabus without clear headings)
    if not subjects:
        topics = _extract_clean_topics_from_text(full_text, max_topics=15)
        if topics:
            subjects.append({
                "subject": f"Semester {semester} Syllabus",
                "topics": topics,
            })

    # If still nothing — the PDF had no extractable English academic content
    if not subjects:
        raise ValueError(
            "Could not extract any academic topics from the uploaded PDF. "
            "Please ensure the PDF contains readable English text (not a scanned image) "
            "and includes the syllabus for the selected semester."
        )

    return subjects


def upload_curriculum_from_pdf_text(
    mentor_id: str,
    full_course_text: str,
    semester: str,
    question_types: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    Store curriculum extracted from a syllabus PDF for a specific semester.
    Topics are extracted directly from the uploaded PDF text (no mock data).
    """
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")
    if not semester:
        raise ValueError("semester is required")

    # Default to MCQ + short if no types selected
    valid_types = {"mcq", "short", "fill_blank", "integer"}
    if not question_types:
        question_types = ["mcq", "short"]
    else:
        question_types = [t for t in question_types if t in valid_types]
        if not question_types:
            question_types = ["mcq", "short"]

    # Parse actual subjects/topics from PDF text for this specific semester
    parsed_subjects = _parse_syllabus_for_semester(full_course_text, semester)

    mentor_data = MENTOR_CURRICULUM.setdefault(mentor_id, {})
    saved_subjects: List[Dict] = []

    for sub_info in parsed_subjects:
        subject = sub_info["subject"]
        topics = sub_info["topics"]
        key = f"{subject.lower()}::{semester.lower()}"
        mentor_data[key] = {
            "subject": subject.lower(),
            "semester": semester.lower(),
            "syllabus_text": full_course_text,
            "scheme_text": "",
            "topics": topics,
            "question_types": question_types,
        }
        saved_subjects.append({
            "subject": subject.lower(),
            "semester": semester.lower(),
            "topics_count": len(topics),
            "topics_preview": topics[:3],  # first 3 topics for preview
        })

    total_subjects = len(saved_subjects)
    return {
        "message": f"Syllabus uploaded successfully. Extracted {total_subjects} subject(s) for Semester {semester}.",
        "mentor_id": mentor_id,
        "semester": semester.lower(),
        "subjects_count": str(total_subjects),
        "subjects": saved_subjects,
        "question_types": question_types,
    }


def curriculum_options_for_mentor(mentor_id: str) -> Dict:
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")

    options = []
    for key, item in MENTOR_CURRICULUM.get(mentor_id, {}).items():
        options.append({
            "key": key,
            "subject": item["subject"],
            "semester": item["semester"],
            "topics_count": len(item.get("topics", [])),
            "topics_preview": item.get("topics", [])[:3],
        })

    return {"mentor_id": mentor_id, "options": options}


def delete_curriculum_entry(mentor_id: str, key: str) -> Dict:
    """Remove a specific subject entry from the mentor's curriculum."""
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")
    mentor_data = MENTOR_CURRICULUM.get(mentor_id, {})
    if key not in mentor_data:
        raise ValueError(f"Curriculum entry '{key}' not found")
    del mentor_data[key]
    return {"message": f"Entry '{key}' removed successfully"}


def _build_questions_from_curriculum(
    subject: str,
    topics: List[str],
    question_types: Optional[List[str]] = None,
) -> List[Dict]:
    """Build a question pool from curriculum topics using the mentor-selected question types."""
    if not topics:
        topics = [subject]
    if not question_types:
        question_types = ["mcq", "short"]

    # Sanitize topics: keep only clean English phrases for question generation
    clean_topics = [t for t in topics if _is_clean_english_topic(t)]
    if not clean_topics:
        clean_topics = topics  # fallback if all filtered out

    picked_topics = clean_topics[:8]  # use up to 8 topics
    generated = []
    difficulties = ["easy", "easy", "medium", "medium", "hard", "hard", "medium", "easy"]

    # Build a readable display name from the subject key (e.g. "data structures" → "Data Structures")
    subject_display = subject.replace("_", " ").replace("::", " — ").title()

    for idx, topic in enumerate(picked_topics, start=1):
        diff = difficulties[idx - 1] if idx - 1 < len(difficulties) else "medium"
        q_type = question_types[(idx - 1) % len(question_types)]
        qid = f"{re.sub(r'[^a-z0-9]', '_', subject.lower())}_{idx}"

        # Capitalize topic for display
        topic_display = topic.strip().capitalize()

        if q_type == "mcq":
            generated.append({
                "id": qid,
                "type": "mcq",
                "ai_generated": True,
                "topic": topic_display,
                "difficulty": diff,
                "question": (
                    f"Which of the following best describes '{topic_display}' "
                    f"as covered in {subject_display}?"
                ),
                "options": [
                    f"{topic_display}: the standard definition and core principle",
                    f"A hardware component unrelated to {subject_display}",
                    f"An optional feature rarely used in {subject_display}",
                    "None of the above",
                ],
                "correct_answer": f"{topic_display}: the standard definition and core principle",
                "model_answer": f"{topic_display}: the standard definition and core principle",
            })

        elif q_type == "short":
            generated.append({
                "id": qid,
                "type": "short",
                "ai_generated": True,
                "topic": topic_display,
                "difficulty": diff,
                "question": (
                    f"Briefly explain the concept of '{topic_display}' and describe "
                    f"one real-world application where it is used in {subject_display}."
                ),
                "correct_answer": f"{topic_display} — definition and application",
                "model_answer": (
                    f"'{topic_display}' is a key concept in {subject_display}. "
                    f"It refers to the study and application of {topic_display.lower()} "
                    f"in practical scenarios within the domain of {subject_display}."
                ),
            })

        elif q_type == "fill_blank":
            generated.append({
                "id": qid,
                "type": "fill_blank",
                "ai_generated": True,
                "topic": topic_display,
                "difficulty": diff,
                "question": (
                    f"In {subject_display}, the term ___ refers to the "
                    f"principle or technique known as '{topic_display}'."
                ),
                "blank_hint": topic_display,
                "correct_answer": topic_display,
                "model_answer": topic_display,
            })

        elif q_type == "integer":
            count = (idx % 4) + 2  # cycles 2, 3, 4, 5
            generated.append({
                "id": qid,
                "type": "integer",
                "ai_generated": True,
                "topic": topic_display,
                "difficulty": diff,
                "question": (
                    f"In {subject_display}, the topic '{topic_display}' "
                    f"is generally divided into how many primary components or phases? "
                    f"(Enter a whole number)"
                ),
                "correct_answer": str(count),
                "model_answer": str(count),
            })

    return generated


def start_mentor_session(
    mentor_id: str,
    student_name: str,
    enrollment_no: str,
    semester: str,
    subject: str,
) -> Dict:
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")
    if not student_name or not enrollment_no or not semester or not subject:
        raise ValueError(
            "mentor_id, student_name, enrollment_no, semester, and subject are required"
        )

    key = f"{subject.lower()}::{semester.lower()}"
    mentor_data = MENTOR_CURRICULUM.get(mentor_id, {})
    curriculum = mentor_data.get(key)
    if not curriculum:
        raise ValueError(
            "No uploaded syllabus/scheme for this subject and semester. Upload first."
        )

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "session_id": session_id,
        "mentor_id": mentor_id,
        "student_name": student_name,
        "enrollment_no": enrollment_no,
        "semester": semester.lower(),
        "subject": subject.lower(),
        "current_difficulty": "medium",
        "asked_questions": [],
        "responses": [],
        "completed": False,
        "question_pool": _build_questions_from_curriculum(
            subject.lower(),
            curriculum["topics"],
            curriculum.get("question_types", ["mcq", "short"]),
        ),
    }
    CLASS_SESSIONS.append(session_id)
    return SESSIONS[session_id]


def mentor_dashboard(mentor_id: str) -> Dict:
    if mentor_id not in MENTORS:
        raise ValueError("Mentor not found")

    reports = []
    for sid in CLASS_SESSIONS:
        session = SESSIONS.get(sid)
        if not session or session.get("mentor_id") != mentor_id or not session["responses"]:
            continue
        reports.append(generate_report(sid))

    uploaded = []
    for key, value in MENTOR_CURRICULUM.get(mentor_id, {}).items():
        uploaded.append(
            {
                "key": key,
                "subject": value["subject"],
                "semester": value["semester"],
                "topics_count": len(value.get("topics", [])),
                "topics_preview": value.get("topics", [])[:3],
            }
        )

    if not reports:
        return {
            "mentor_id": mentor_id,
            "uploaded_curriculum": uploaded,
            "students_assessed": 0,
            "message": "No student responses yet",
        }

    avg_accuracy = sum(r["overall_accuracy_percent"] for r in reports) / len(reports)
    weak_topics = Counter(topic for report in reports for topic in report["weaknesses"])

    return {
        "mentor_id": mentor_id,
        "uploaded_curriculum": uploaded,
        "students_assessed": len(reports),
        "average_accuracy_percent": round(avg_accuracy, 2),
        "common_weak_topics": weak_topics.most_common(5),
    }


def _filter_candidates(subject: str, difficulty: str, asked: List[str]) -> List[Dict]:
    return [
        q
        for q in QUESTION_BANK[subject]
        if q["difficulty"] == difficulty and q["id"] not in asked
    ]


def _question_pool_for_session(session: Dict) -> List[Dict]:
    """Return the PDF-backed question pool. Never fall back to the static question bank."""
    pool = session.get("question_pool")
    if not pool:
        raise ValueError(
            "No question pool found for this session. "
            "The session must be started through a mentor with an uploaded syllabus."
        )
    return pool


def _adjust_difficulty(current: str, was_correct: bool) -> str:
    idx = DIFFICULTY_ORDER.index(current)
    if was_correct and idx < len(DIFFICULTY_ORDER) - 1:
        return DIFFICULTY_ORDER[idx + 1]
    if not was_correct and idx > 0:
        return DIFFICULTY_ORDER[idx - 1]
    return current


def _sanitize_question(question: Dict) -> Dict:
    payload = {
        "id": question["id"],
        "type": question["type"],
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "question": question["question"],
    }
    if question["type"] == "mcq":
        payload["options"] = question["options"]
    return payload


def next_question(session_id: str) -> Optional[Dict]:
    session = SESSIONS.get(session_id)
    if not session:
        raise ValueError("Session not found")

    if len(session["asked_questions"]) >= 6:
        session["completed"] = True
        return None

    subject = session["subject"]
    question_pool = _question_pool_for_session(session)
    difficulty = session["current_difficulty"]
    candidates = [
        q
        for q in question_pool
        if q["difficulty"] == difficulty and q["id"] not in session["asked_questions"]
    ]

    # fallback if exact difficulty exhausted
    if not candidates:
        remaining = [q for q in question_pool if q["id"] not in session["asked_questions"]]
        if not remaining:
            session["completed"] = True
            return None
        candidates = remaining

    question = random.choice(candidates)
    session["asked_questions"].append(question["id"])
    return _sanitize_question(question)


def submit_answer(session_id: str, question_id: str, answer: str, confidence: str) -> Dict:
    session = SESSIONS.get(session_id)
    if not session:
        raise ValueError("Session not found")
    if confidence.lower() not in {"low", "medium", "high"}:
        raise ValueError("Confidence must be Low, Medium, or High")

    question = next((q for q in _question_pool_for_session(session) if q["id"] == question_id), None)
    if not question:
        raise ValueError("Question not found")

    if question["type"] == "mcq":
        is_correct, similarity = evaluate_mcq(answer, question["correct_answer"])
    elif question["type"] == "fill_blank":
        is_correct, similarity = evaluate_fill_blank(answer, question["correct_answer"])
    elif question["type"] == "integer":
        is_correct, similarity = evaluate_integer(answer, question["correct_answer"])
    else:
        is_correct, similarity = evaluate_subjective(answer, question["model_answer"])

    score_parts = calculate_weighted_score(
        is_correct=is_correct,
        confidence=confidence,
        difficulty=question["difficulty"],
    )
    interpretation = confidence_bucket(is_correct, confidence)

    response = {
        "question_id": question_id,
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "student_answer": answer,
        "correct_answer": question["correct_answer"],
        "confidence": confidence.lower(),
        "is_correct": is_correct,
        "similarity_score": similarity,
        "interpretation": interpretation,
        "score_breakdown": score_parts,
    }
    session["responses"].append(response)
    session["current_difficulty"] = _adjust_difficulty(
        session["current_difficulty"], is_correct
    )
    return response


def generate_report(session_id: str) -> Dict:
    session = SESSIONS.get(session_id)
    if not session:
        raise ValueError("Session not found")

    responses = session["responses"]
    if not responses:
        return {
            "session_id": session_id,
            "student_name": session["student_name"],
            "subject": session["subject"],
            "message": "No responses yet",
        }

    total_score = sum(r["score_breakdown"]["total"] for r in responses)
    accuracy = round(
        (sum(1 for r in responses if r["is_correct"]) / len(responses)) * 100, 2
    )

    topic_perf = defaultdict(lambda: {"attempts": 0, "correct": 0, "score": 0})
    confidence_map = Counter(r["interpretation"] for r in responses)

    for r in responses:
        topic = topic_perf[r["topic"]]
        topic["attempts"] += 1
        topic["correct"] += int(r["is_correct"])
        topic["score"] += r["score_breakdown"]["total"]

    strengths = []
    weaknesses = []
    misconceptions = []
    for topic, stats in topic_perf.items():
        topic_acc = stats["correct"] / stats["attempts"]
        if topic_acc >= 0.75:
            strengths.append(topic)
        elif topic_acc <= 0.4:
            weaknesses.append(topic)
    misconceptions = [
        r["topic"]
        for r in responses
        if r["interpretation"] == "misconception"
    ]

    return {
        "session_id": session_id,
        "student_name": session["student_name"],
        "enrollment_no": session.get("enrollment_no"),
        "semester": session.get("semester"),
        "mentor_id": session.get("mentor_id"),
        "subject": session["subject"],
        "questions_attempted": len(responses),
        "overall_accuracy_percent": accuracy,
        "total_score": total_score,
        "topic_wise_performance": topic_perf,
        "confidence_analysis": dict(confidence_map),
        "strengths": sorted(set(strengths)),
        "weaknesses": sorted(set(weaknesses)),
        "overconfident_topics": sorted(set(misconceptions)),
        "responses": responses,
    }


def class_dashboard() -> Dict:
    valid_reports = []
    for sid in CLASS_SESSIONS:
        if sid in SESSIONS and SESSIONS[sid]["responses"]:
            valid_reports.append(generate_report(sid))

    if not valid_reports:
        return {"message": "No class data available yet", "students_assessed": 0}

    avg_accuracy = sum(r["overall_accuracy_percent"] for r in valid_reports) / len(
        valid_reports
    )
    avg_score = sum(r["total_score"] for r in valid_reports) / len(valid_reports)
    common_weak_topics = Counter(
        topic for report in valid_reports for topic in report["weaknesses"]
    )
    common_overconf = Counter(
        topic for report in valid_reports for topic in report["overconfident_topics"]
    )

    return {
        "students_assessed": len(valid_reports),
        "average_accuracy_percent": round(avg_accuracy, 2),
        "average_total_score": round(avg_score, 2),
        "most_common_weak_topics": common_weak_topics.most_common(5),
        "most_common_overconfidence_topics": common_overconf.most_common(5),
    }