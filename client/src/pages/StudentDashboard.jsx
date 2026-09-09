import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/api';
import { Send, PlayCircle, Search, User } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const StudentDashboard = () => {
  // Auto-read from localStorage (set during login)
  const authName       = localStorage.getItem('auth_name')       || '';
  const authIdentifier = localStorage.getItem('auth_identifier') || '';

  const [mentorId, setMentorId] = useState(localStorage.getItem('student_mentor_id') || 'MTR001');
  const [studentDetails, setStudentDetails] = useState({
    name:       authName,
    enrollment: authIdentifier,
    semester:   '',
    subject:    '',
  });

  const [rawOptions, setRawOptions] = useState([]);
  const [options, setOptions] = useState({ semesters: [], subjects: [] });
  const [infoStatus, setInfoStatus] = useState({ type: '', msg: '' });

  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [confidence, setConfidence] = useState('medium');
  const [feedback, setFeedback] = useState('');

  const [report, setReport] = useState(null);

  const loadOptions = useCallback(async (targetMentorId) => {
    const target = (targetMentorId !== undefined && typeof targetMentorId === 'string') ? targetMentorId : mentorId;
    if (!target) {
      setInfoStatus({ type: 'error', msg: 'Enter mentor ID' });
      return;
    }
    try {
      const { data } = await api.get(`/mentor/curriculum/options?mentor_id=${target.trim()}`);
      if (data.error || !data.options || !data.options.length) {
        setInfoStatus({ type: 'error', msg: data.error || `No uploaded curriculum found for mentor ID '${target}'.` });
      } else {
        setRawOptions(data.options);
        const sems = ['1', '2', '3', '4', '5', '6', '7', '8'];
        const availableSems = [...new Set(data.options.map(o => String(o.semester)))];
        const activeSem = availableSems.length > 0 ? availableSems[0] : sems[0];
        const subs = data.options.filter((o) => String(o.semester) === activeSem).map((o) => o.subject);
        setOptions({ semesters: sems, subjects: subs });
        setStudentDetails((prev) => ({ ...prev, semester: activeSem, subject: subs[0] || '' }));
        setInfoStatus({ type: 'success', msg: `Loaded ${data.options.length} subject(s) for mentor ${target.trim()}. Selected Semester ${activeSem}.` });
        localStorage.setItem('student_mentor_id', target.trim());
      }
    } catch (err) {
      setInfoStatus({ type: 'error', msg: err?.response?.data?.error || 'Failed to load options for mentor.' });
    }
  }, [mentorId]);

  useEffect(() => {
    const initialMentor = localStorage.getItem('student_mentor_id') || 'MTR001';
    loadOptions(initialMentor);
  }, [loadOptions]);


  const startSession = async () => {
    const { name, enrollment, semester, subject } = studentDetails;
    if (!mentorId || !name || !enrollment || !semester || !subject) {
      setInfoStatus({ type: 'error', msg: 'Please fill all student details.' });
      return;
    }

    try {
      const payload = { mentor_id: mentorId, student_name: name, enrollment_no: enrollment, semester, subject };
      const { data } = await api.post('/student/session/start', payload);

      if (data.error) {
        setInfoStatus({ type: 'error', msg: data.error });
      } else {
        setSessionId(data.session_id);
        setSessionStarted(true);
        fetchNextQuestion(data.session_id);
      }
    } catch (err) {
      setInfoStatus({ type: 'error', msg: 'Failed to start session' });
    }
  };

  const fetchNextQuestion = async (sid) => {
    try {
      const { data } = await api.get(`/question/next?session_id=${sid}`);
      if (data.question) {
        setQuestion(data.question);
        setAnswer('');
      } else {
        setQuestion(null);
        fetchReport(sid);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const submitAnswer = async () => {
    if (!question || !sessionId) return;

    if (!answer.trim()) {
      alert('Please provide an answer');
      return;
    }

    try {
      const { data } = await api.post('/answer/submit', {
        session_id: sessionId,
        question_id: question.id,
        answer,
        confidence,
      });

      if (data.error) {
        alert(data.error);
        return;
      }

      const score = data.evaluation?.score_breakdown?.total ?? 0;
      const interpretation = data.evaluation?.interpretation?.replace(/_/g, ' ') ?? 'evaluation complete';
      setFeedback(`Result: ${data.evaluation.is_correct ? 'Correct' : 'Wrong'} • ${interpretation} • Score ${score}`);

      setTimeout(() => {
        setFeedback('');
        fetchNextQuestion(sessionId);
      }, 1500);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchReport = async (sid) => {
    try {
      const { data } = await api.get(`/report/${sid}`);
      setReport(data);
    } catch (err) {
      console.error(err);
    }
  };

  if (report) {
    const topicData = Object.entries(report.topic_wise_performance || {}).map(([name, data]) => ({
      name,
      accuracy: Math.round((data.correct / Math.max(1, data.attempts)) * 100),
    }));

    const confidenceColors = {
      strong_knowledge: '#10b981',
      developing: '#3b82f6',
      underconfident: '#f59e0b',
      weak_understanding: '#ef4444',
      misconception: '#8b5cf6',
    };

    const confidenceData = Object.entries(report.confidence_analysis || {}).map(([name, val]) => ({
      name: name.replace('_', ' ').toUpperCase(),
      value: val,
      color: confidenceColors[name] || '#8884d8',
    }));

    return (
      <main className="container">
        <h1>Performance Report</h1>
        <p className="sub">Assessment complete. Review your accuracy, confidence profile, and topic-level performance below.</p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <section className="card" style={{ marginBottom: 0 }}>
            <h2>Overview</h2>
            <div style={{ display: 'flex', justifyContent: 'space-around', margin: '2rem 0' }}>
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>{report.overall_accuracy_percent}%</span>
                <p style={{ color: '#94a3b8' }}>Accuracy</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--secondary)' }}>{report.total_score}</span>
                <p style={{ color: '#94a3b8' }}>Total Score</p>
              </div>
            </div>

            <div style={{ marginTop: '1rem' }}>
              <h4 style={{ color: '#10b981' }}>Strengths:</h4>
              <p>{report.strengths?.length > 0 ? report.strengths.join(', ') : 'None identified yet'}</p>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4 style={{ color: '#ef4444' }}>Weaknesses:</h4>
              <p>{report.weaknesses?.length > 0 ? report.weaknesses.join(', ') : 'None identified yet'}</p>
            </div>
          </section>

          <section className="card" style={{ marginBottom: 0 }}>
            <h2>Confidence Mapping & Accuracy</h2>
            {confidenceData.length > 0 ? (
              <div style={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={confidenceData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {confidenceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p>No confidence data generated</p>
            )}
          </section>
        </div>

        <section className="card">
          <h2>Topic Accuracy Breakdown</h2>
          <div style={{ height: 300, marginTop: '2rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#cbd5e1" tick={{ fill: '#cbd5e1' }} />
                <YAxis stroke="#cbd5e1" tick={{ fill: '#cbd5e1' }} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="accuracy" fill="var(--primary)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="container">
      <h1>Student Dashboard</h1>
      <p className="sub">Enter your details and begin an AI-generated assessment based on confidence, accuracy, and adaptive difficulty.</p>

      {!sessionStarted ? (
        <>
          <section className="card">
            <h2>Assessment Methodology</h2>
            <p className="sub" style={{ marginBottom: '1rem' }}>
              This student portal follows an AI-driven assessment workflow designed to measure accuracy, confidence, and conceptual understanding.
            </p>

            <div className="feature-grid">
              <div className="feature-card">
                <h3>Phase 1: Question Bank Creation</h3>
                <p>Create subject-wise question banks and tag questions by topic, difficulty, and type.</p>
              </div>
              <div className="feature-card">
                <h3>Phase 2: AI Question Generator</h3>
                <p>Use AI to generate adaptive questions aligned with the selected syllabus and subject context.</p>
              </div>
              <div className="feature-card">
                <h3>Phase 3: Student Interaction Module</h3>
                <p>Provide a student interface for answering questions, choosing confidence levels, and progressing through the assessment.</p>
              </div>
            </div>

            <div className="feature-grid" style={{ marginTop: '1rem' }}>
              <div className="feature-card">
                <h3>Phase 4: Answer Evaluation Engine</h3>
                <p><strong>Case 1: Objective Questions (MCQ)</strong> — direct comparison with the correct answer.</p>
                <p><strong>Case 2: Subjective Questions</strong> — use AI/NLP to evaluate relevance, completeness, and conceptual accuracy.</p>
              </div>
              <div className="feature-card">
                <h3>Phase 5: Confidence Analysis</h3>
                <p><strong>Correct + High Confidence</strong> → Strong knowledge</p>
                <p><strong>Correct + Low Confidence</strong> → Needs confidence improvement</p>
                <p><strong>Wrong + High Confidence</strong> → Misconception</p>
                <p><strong>Wrong + Low Confidence</strong> → Weak understanding</p>
              </div>
              <div className="feature-card">
                <h3>Phase 6: Scoring Mechanism</h3>
                <p>Score is based on accuracy, confidence level, and difficulty level.</p>
                <p><strong>Example:</strong> Correct + High Confidence → High score; Wrong + High Confidence → Negative weight for deeper insight.</p>
              </div>
            </div>

            <div className="feature-card" style={{ marginTop: '1rem' }}>
              <h3>Phase 7: Report Generation</h3>
              <p>The system generates subject-wise score, topic-wise performance, confidence analysis, strengths, and weaknesses.</p>
              <p><strong>Example output:</strong> Strong in Data Structures, weak in DBMS normalization, and overconfident in Networking.</p>
            </div>
          </section>

          <section className="card">
            <h2>Student Information</h2>

            {/* Logged-in student info (read-only) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.65rem 1rem', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: '10px', marginBottom: '1.25rem' }}>
              <User size={18} color="var(--primary)" />
              <div>
                <div style={{ fontWeight: 600, color: '#fff' }}>{authName}</div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Enrollment: {authIdentifier}</div>
              </div>
            </div>

            {/* Mentor ID — student enters the faculty whose syllabus they want */}
            <div className="row" style={{ display: 'flex', flexDirection: 'row', gap: '1rem', alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <label>Faculty / Mentor ID <span style={{ color: '#94a3b8', fontWeight: 400, fontSize: '0.8rem' }}>(to load their syllabus)</span></label>
                <input value={mentorId} onChange={(e) => setMentorId(e.target.value)} type="text" placeholder="e.g. MTR001" />
              </div>
              <button onClick={loadOptions} style={{ width: 'auto', marginBottom: '2px' }} className="secondary">
                <Search size={18} /> Load Syllabus
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
              <div className="row">
                <label>Semester</label>
                <select
                  value={studentDetails.semester}
                  onChange={(e) => {
                    const sem = e.target.value;
                    const subs = rawOptions.filter((o) => String(o.semester) === sem).map((o) => o.subject);
                    setOptions((prev) => ({ ...prev, subjects: subs }));
                    setStudentDetails({ ...studentDetails, semester: sem, subject: subs[0] || '' });
                  }}
                >
                  {options.semesters.length === 0 && <option value="">Load syllabus first</option>}
                  {options.semesters.map((opt) => (
                    <option key={opt} value={opt}>Semester {opt}</option>
                  ))}
                </select>
              </div>
              <div className="row">
                <label>Subject</label>
                <select value={studentDetails.subject} onChange={(e) => setStudentDetails({ ...studentDetails, subject: e.target.value })}>
                  {options.subjects.length === 0 && <option value="">Load syllabus first</option>}
                  {options.subjects.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            </div>

            <button onClick={startSession} style={{ marginTop: '1rem' }}>
              <PlayCircle size={18} /> Start Assessment
            </button>

            {infoStatus.msg && <div className={`status ${infoStatus.type}`}>{infoStatus.msg}</div>}
          </section>
        </>
      ) : (
        question && (
          <section className="card">
            <h2 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
              <span>Question</span>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className={`question-type-tag ${question.type}`}>
                  {question.type === 'mcq' && '🔘 MCQ'}
                  {question.type === 'short' && '✍️ Short Answer'}
                  {question.type === 'fill_blank' && '🔲 Fill Blank'}
                  {question.type === 'integer' && '🔢 Integer'}
                </span>
                <span style={{ fontSize: '0.9rem', padding: '0.2rem 0.5rem', background: 'rgba(99, 102, 241, 0.2)', borderRadius: '4px', color: 'var(--primary)' }}>
                  {question.difficulty.toUpperCase()}
                </span>
              </div>
            </h2>
            <p style={{ color: '#cbd5e1', marginBottom: '1.5rem', fontSize: '0.9rem' }}>Topic: {question.topic}</p>

            <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem' }}>{question.question}</p>

            {/* ── MCQ ── */}
            {question.type === 'mcq' && (
              <div className="row" style={{ gap: '0.5rem' }}>
                {question.options.map((opt, i) => (
                  <label key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', background: 'rgba(255,255,255,0.05)', padding: '0.75rem', borderRadius: '8px', border: answer === opt ? '1px solid var(--primary)' : '1px solid transparent' }}>
                    <input type="radio" name="mcq" value={opt} onChange={(e) => setAnswer(e.target.value)} checked={answer === opt} style={{ width: 'auto' }} />
                    {opt}
                  </label>
                ))}
              </div>
            )}

            {/* ── Short Answer ── */}
            {question.type === 'short' && (
              <div className="row">
                <label>Your Answer</label>
                <textarea rows={4} value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Type your detailed answer here..." />
              </div>
            )}

            {/* ── Fill in the Blank ── */}
            {question.type === 'fill_blank' && (
              <div className="row">
                <label style={{ marginBottom: '0.75rem' }}>Fill in the blank:</label>
                {/* Show sentence with blank highlighted */}
                <div className="fill-blank-sentence">
                  {question.question.split('___').map((part, i, arr) => (
                    <span key={i}>
                      {part}
                      {i < arr.length - 1 && (
                        <span className="fill-blank-underline">
                          {answer || '\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0'}
                        </span>
                      )}
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  className="fill-blank-input"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                />
              </div>
            )}

            {/* ── Integer / Numerical ── */}
            {question.type === 'integer' && (
              <div className="row">
                <label style={{ marginBottom: '0.75rem' }}>Enter a number:</label>
                <div className="integer-input-wrap">
                  <input
                    type="number"
                    className="integer-input"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="0"
                    min="0"
                    step="1"
                  />
                  <span className="integer-unit-hint">(whole number only)</span>
                </div>
              </div>
            )}

            <div className="row" style={{ marginTop: '1rem' }}>
              <label>Confidence Level</label>
              <select value={confidence} onChange={(e) => setConfidence(e.target.value)}>
                <option value="low">Low (I'm guessing)</option>
                <option value="medium">Medium (I'm fairly sure)</option>
                <option value="high">High (I'm absolutely sure)</option>
              </select>
            </div>

            <button onClick={submitAnswer} id="btn-submit-answer">
              Submit Answer <Send size={18} />
            </button>

            {feedback && (
              <div className="status" style={{ background: 'rgba(255, 255, 255, 0.1)', marginTop: '1rem' }}>
                {feedback}
              </div>
            )}
          </section>
        )
      )}
    </main>
  );
};

export default StudentDashboard;
