// MongoDB Collections Schema (Reference Document)
// ================================================
// This file documents the MongoDB collections used in this project.
// No SQL migrations needed — MongoDB is schema-flexible.

/*
 * DATABASE: ai_student_performance
 *
 * ── Collection: users ──────────────────────────────────────────
 * {
 *   _id:           ObjectId,          // auto-generated
 *   identifier:    "MTR001",          // faculty ID or enrollment no.
 *   name:          "Faculty Name",
 *   role:          "faculty" | "student",
 *   password_hash: "$2b$12$...",      // bcrypt 12 rounds
 *   created_at:    ISODate,
 *   is_active:     true | false
 * }
 * Index: { identifier: 1, role: 1 } — unique
 *
 * ── Collection: curriculum (future) ────────────────────────────
 * {
 *   _id:           ObjectId,
 *   mentor_id:     "MTR001",
 *   subject:       "Data Structures",
 *   semester:      "3",
 *   topics:        ["Stacks", "Trees", ...],
 *   question_types: ["mcq", "short"],
 *   uploaded_at:   ISODate
 * }
 *
 * ── Collection: sessions (future) ──────────────────────────────
 * {
 *   _id:             ObjectId,
 *   session_id:      "uuid-...",
 *   student_name:    "Alice",
 *   enrollment_no:   "STU001",
 *   mentor_id:       "MTR001",
 *   subject:         "Data Structures",
 *   semester:        "3",
 *   responses:       [...],
 *   completed:       false,
 *   created_at:      ISODate
 * }
 */
