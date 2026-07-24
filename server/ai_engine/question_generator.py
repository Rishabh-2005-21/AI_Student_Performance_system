"""
Gemini-powered question generator for Faculty Question Bank.
Falls back to rule-based generation if Gemini is unavailable.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Dict, List, Optional

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ---------------------------------------------------------------------------
# Gemini client (lazy init)
# ---------------------------------------------------------------------------

_gemini_model = None


def _get_gemini_model():
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        print("[Gemini] Model loaded: gemini-1.5-flash")
        return _gemini_model
    except Exception as exc:
        print(f"[Gemini] Failed to init: {exc}")
        return None


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(
    text: str,
    subject: str,
    question_types: List[str],
    difficulties: List[str],
    count: int,
) -> str:
    type_desc = {
        "mcq": "Multiple Choice Question with 4 options (A, B, C, D) and one correct answer",
        "fill_blank": "Fill in the Blank — a sentence with one blank, give the correct word/phrase",
        "short": "Short Answer — a question requiring a brief 1-3 sentence explanation",
        "integer": "Integer/Numerical — a question with an exact numerical answer",
    }
    types_info = "\n".join(
        f'  - "{t}": {type_desc.get(t, t)}' for t in question_types
    )
    diffs_str = ", ".join(difficulties)

    return f"""You are an expert academic question paper setter.

Based on the following syllabus/document content, generate exactly {count} questions.
Subject: {subject}
Requested question types: {", ".join(question_types)}
Requested difficulty levels: {diffs_str}

--- DOCUMENT CONTENT START ---
{text[:6000]}
--- DOCUMENT CONTENT END ---

INSTRUCTIONS:
1. Generate exactly {count} questions spread across the requested types and difficulties.
2. Each question MUST be directly based on the document content above.
3. For MCQ: provide exactly 4 options labelled A, B, C, D and specify the correct one.
4. For fill_blank: use "___" to indicate the blank.
5. Make questions academically rigorous and specific to the content.
6. Distribute difficulties: use these levels from the list: {diffs_str}

Return ONLY a valid JSON array (no markdown, no explanation) with this exact structure:
[
  {{
    "question": "What is ...?",
    "type": "mcq",
    "difficulty": "medium",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "correct_answer": "A. option1",
    "topic": "extracted topic name"
  }},
  {{
    "question": "The process of ___ involves ...",
    "type": "fill_blank",
    "difficulty": "easy",
    "options": [],
    "correct_answer": "photosynthesis",
    "topic": "topic name"
  }},
  {{
    "question": "Explain briefly ...",
    "type": "short",
    "difficulty": "hard",
    "options": [],
    "correct_answer": "Brief model answer here",
    "topic": "topic name"
  }}
]

Generate {count} questions now:"""


# ---------------------------------------------------------------------------
# Gemini generation
# ---------------------------------------------------------------------------

def _generate_with_gemini(
    text: str,
    subject: str,
    question_types: List[str],
    difficulties: List[str],
    count: int,
) -> Optional[List[Dict]]:
    model = _get_gemini_model()
    if not model:
        return None
    try:
        prompt = _build_prompt(text, subject, question_types, difficulties, count)
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code blocks if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        questions = json.loads(raw)
        if not isinstance(questions, list):
            return None

        result = []
        for q in questions:
            if not isinstance(q, dict):
                continue
            qtype = q.get("type", "short")
            if qtype not in ("mcq", "fill_blank", "short", "integer"):
                qtype = "short"
            diff = q.get("difficulty", "medium")
            if diff not in ("easy", "medium", "hard"):
                diff = "medium"
            result.append({
                "id": str(uuid.uuid4()),
                "question": str(q.get("question", "")).strip(),
                "type": qtype,
                "difficulty": diff,
                "options": q.get("options", []) if qtype == "mcq" else [],
                "correct_answer": str(q.get("correct_answer", "")).strip(),
                "topic": str(q.get("topic", subject)).strip(),
                "status": "pending",
                "source": "ai_gemini",
            })
        return result if result else None
    except Exception as exc:
        print(f"[Gemini] Generation error: {exc}")
        return None


# ---------------------------------------------------------------------------
# Rule-based fallback generator
# ---------------------------------------------------------------------------

def _generate_rule_based(
    text: str,
    subject: str,
    question_types: List[str],
    difficulties: List[str],
    count: int,
) -> List[Dict]:
    """Generate questions using rule-based templates from extracted topics."""

    # Extract candidate topics from the text
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    topics: List[str] = []
    seen = set()

    for line in lines:
        # Look for heading-like lines (2–8 words, starts with capital)
        words = line.split()
        if 2 <= len(words) <= 8 and line[0].isupper():
            clean = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            if len(clean) >= 6 and clean.lower() not in seen:
                seen.add(clean.lower())
                topics.append(clean)
        if len(topics) >= 30:
            break

    if not topics:
        # Fallback: split on punctuation
        parts = re.split(r"[.,;:\n]+", text)
        for p in parts:
            p = p.strip()
            if 6 <= len(p) <= 60 and any(c.isalpha() for c in p):
                clean = p.strip()
                if clean.lower() not in seen:
                    seen.add(clean.lower())
                    topics.append(clean)
            if len(topics) >= 20:
                break

    if not topics:
        topics = [subject.title()]

    # Build questions
    questions: List[Dict] = []
    diff_cycle = difficulties * (count // max(len(difficulties), 1) + 1)
    type_cycle  = question_types * (count // max(len(question_types), 1) + 1)

    for i in range(count):
        topic = topics[i % len(topics)].strip().capitalize()
        qtype = type_cycle[i]
        diff  = diff_cycle[i]

        if qtype == "mcq":
            q = {
                "id": str(uuid.uuid4()),
                "question": f"Which of the following best describes '{topic}'?",
                "type": "mcq",
                "difficulty": diff,
                "options": [
                    f"A. {topic} is a fundamental concept involving core principles",
                    f"B. {topic} refers to an unrelated external mechanism",
                    f"C. {topic} is only applicable in theoretical scenarios",
                    f"D. {topic} has no practical significance",
                ],
                "correct_answer": f"A. {topic} is a fundamental concept involving core principles",
                "topic": topic,
                "status": "pending",
                "source": "rule_based",
            }
        elif qtype == "fill_blank":
            q = {
                "id": str(uuid.uuid4()),
                "question": f"The concept of ___ is central to understanding {topic}.",
                "type": "fill_blank",
                "difficulty": diff,
                "options": [],
                "correct_answer": topic,
                "topic": topic,
                "status": "pending",
                "source": "rule_based",
            }
        elif qtype == "integer":
            q = {
                "id": str(uuid.uuid4()),
                "question": f"How many key components are typically associated with {topic}? (Enter a number)",
                "type": "integer",
                "difficulty": diff,
                "options": [],
                "correct_answer": "3",
                "topic": topic,
                "status": "pending",
                "source": "rule_based",
            }
        else:  # short
            q = {
                "id": str(uuid.uuid4()),
                "question": f"Briefly explain the significance of '{topic}' in this subject.",
                "type": "short",
                "difficulty": diff,
                "options": [],
                "correct_answer": f"{topic} is significant because it forms a core part of the subject curriculum.",
                "topic": topic,
                "status": "pending",
                "source": "rule_based",
            }
        questions.append(q)

    return questions


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_questions(
    text: str,
    subject: str,
    question_types: Optional[List[str]] = None,
    difficulties: Optional[List[str]] = None,
    count: int = 10,
) -> Dict:
    """
    Generate questions from document text.
    Tries Gemini first, falls back to rule-based if unavailable.
    Returns: { "questions": [...], "source": "gemini" | "rule_based" | "fallback" }
    """
    if not question_types:
        question_types = ["mcq", "short"]
    if not difficulties:
        difficulties = ["easy", "medium", "hard"]

    count = max(1, min(count, 50))  # clamp 1–50

    # Try Gemini
    questions = _generate_with_gemini(text, subject, question_types, difficulties, count)
    if questions:
        return {"questions": questions, "source": "gemini", "count": len(questions)}

    # Rule-based fallback
    questions = _generate_rule_based(text, subject, question_types, difficulties, count)
    return {"questions": questions, "source": "rule_based", "count": len(questions)}
