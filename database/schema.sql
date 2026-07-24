CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    role ENUM('student', 'faculty', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    topic_id INT NOT NULL,
    question_type ENUM('mcq', 'short') NOT NULL,
    difficulty ENUM('easy', 'medium', 'hard') NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    model_answer TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS assessment_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_id INT NOT NULL,
    student_answer TEXT NOT NULL,
    confidence ENUM('low', 'medium', 'high') NOT NULL,
    is_correct BOOLEAN NOT NULL,
    similarity_score DECIMAL(4,2),
    score_total INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);