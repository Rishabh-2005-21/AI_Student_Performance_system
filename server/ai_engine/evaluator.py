"""Answer evaluation utilities for objective, subjective, fill-blank, and integer questions."""

from __future__ import annotations

import re
import os
from difflib import SequenceMatcher
from typing import Dict, Tuple

# Try importing openai for AI/NLP evaluation gracefully
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


CONFIDENCE_TO_VALUE = {"low": 1, "medium": 2, "high": 3}
DIFFICULTY_TO_WEIGHT = {"easy": 5, "medium": 10, "hard": 15}


def normalize_text(text: str) -> str:
    """Normalize text by lowercasing and collapsing whitespace."""
    if not text:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def evaluate_mcq(student_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """Evaluate MCQ answers with strict equality."""
    is_correct = normalize_text(student_answer) == normalize_text(correct_answer)
    return is_correct, 1.0 if is_correct else 0.0


def evaluate_subjective(student_answer: str, model_answer: str) -> Tuple[bool, float]:
    """
    Evaluate subjective answers with lexical similarity or OpenAI NLP model if configured.
    """
    s_answer = normalize_text(student_answer)
    m_answer = normalize_text(model_answer)
    if not s_answer or not m_answer:
        return False, 0.0

    # Real AI/NLP integration hook (OpenAI / BERT structure)
    api_key = os.environ.get("OPENAI_API_KEY")
    if HAS_OPENAI and api_key:
        try:
            openai.api_key = api_key
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a strict academic evaluator. Output ONLY a similarity score between 0.0 and 1.0 comparing the student's answer to the model answer based on conceptual accuracy."},
                    {"role": "user", "content": f"Model Answer: {m_answer}\nStudent Answer: {s_answer}"}
                ],
                temperature=0.0
            )
            score = float(response.choices[0].message.content.strip())
            return score >= 0.6, round(score, 2)
        except Exception as e:
            print(f"OpenAI fallback due to error: {e}")
            pass

    # Fallback Lexical Evaluation if no API key is provided
    ratio = SequenceMatcher(None, s_answer, m_answer).ratio()
    is_correct = ratio >= 0.6
    return is_correct, round(ratio, 2)


def evaluate_fill_blank(student_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """
    Evaluate fill-in-the-blank answers with high-threshold fuzzy matching.
    Requires >= 0.8 similarity to be considered correct.
    """
    s_answer = normalize_text(student_answer)
    c_answer = normalize_text(correct_answer)
    if not s_answer or not c_answer:
        return False, 0.0
    # Exact match first
    if s_answer == c_answer:
        return True, 1.0
    # Fuzzy match with high threshold for fill-in-blank
    ratio = SequenceMatcher(None, s_answer, c_answer).ratio()
    is_correct = ratio >= 0.8
    return is_correct, round(ratio, 2)


def evaluate_integer(student_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """
    Evaluate integer/numerical answers with exact integer comparison.
    Both student and correct answers are parsed as integers.
    """
    try:
        student_int = int(str(student_answer).strip())
        correct_int = int(str(correct_answer).strip())
        is_correct = student_int == correct_int
        return is_correct, 1.0 if is_correct else 0.0
    except (ValueError, TypeError):
        # If not a valid integer, try string match as fallback
        s_clean = normalize_text(student_answer)
        c_clean = normalize_text(correct_answer)
        is_correct = s_clean == c_clean
        return is_correct, 1.0 if is_correct else 0.0


def confidence_bucket(is_correct: bool, confidence: str) -> str:
    """Map correctness + confidence to knowledge interpretation."""
    c = confidence.lower()
    if is_correct and c == "high":
        return "strong_knowledge"
    if is_correct and c == "low":
        return "underconfident"
    if not is_correct and c == "high":
        return "misconception"
    if not is_correct and c == "low":
        return "weak_understanding"
    return "developing"


def calculate_weighted_score(
    is_correct: bool, confidence: str, difficulty: str
) -> Dict[str, int]:
    """Compute score components and total score."""
    conf = confidence.lower()
    diff = difficulty.lower()

    accuracy_score = 60 if is_correct else 0

    if is_correct and conf == "high":
        confidence_score = 20
    elif is_correct and conf == "medium":
        confidence_score = 12
    elif is_correct and conf == "low":
        confidence_score = 5
    elif not is_correct and conf == "high":
        confidence_score = -15
    else:
        confidence_score = 0

    difficulty_score = DIFFICULTY_TO_WEIGHT.get(diff, 5)

    total = accuracy_score + confidence_score + difficulty_score
    return {
        "accuracy": accuracy_score,
        "confidence": confidence_score,
        "difficulty": difficulty_score,
        "total": total,
    }