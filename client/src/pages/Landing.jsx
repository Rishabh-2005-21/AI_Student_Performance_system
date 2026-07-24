import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Brain, BarChart3, ShieldCheck } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <main className="container hero">
      <section className="card hero-card">
        <h1>AI-Powered Real-Time Student Assessment</h1>
        <p className="sub">
          A smart assessment engine that asks adaptive questions, evaluates answers in real time,
          measures student confidence, and generates detailed subject-wise performance reports.
        </p>

        <div className="hero-actions">
          <button
            onClick={() => navigate('/login?role=student')}
            style={{ width: 'auto', padding: '1rem 2rem', fontSize: '1.1rem' }}
          >
            <Sparkles size={20} />
            Start Assessment
          </button>
          <button
            className="secondary"
            onClick={() => navigate('/login?role=faculty')}
            style={{ width: 'auto', padding: '1rem 2rem', fontSize: '1.1rem' }}
          >
            Faculty Portal
            <ArrowRight size={20} />
          </button>
        </div>
      </section>

      <section className="card">
        <h2>How the system works</h2>
        <div className="feature-grid">
          <article className="feature-card">
            <h3><Brain size={18} /> Phase 1</h3>
            <p>Question Bank Creation</p>
            <span>Subject-wise question pools with topic and difficulty tags.</span>
          </article>
          <article className="feature-card">
            <h3><Sparkles size={18} /> Phase 2</h3>
            <p>AI Question Generation</p>
            <span>Questions are selected adaptively based on the student’s performance.</span>
          </article>
          <article className="feature-card">
            <h3><ShieldCheck size={18} /> Phase 3</h3>
            <p>Confidence-Based Interaction</p>
            <span>Students answer questions and indicate whether they feel low, medium, or high confidence.</span>
          </article>
          <article className="feature-card">
            <h3><BarChart3 size={18} /> Phase 4</h3>
            <p>Report Generation</p>
            <span>Scores, strengths, weaknesses, and overconfidence insights are summarized for faculty and students.</span>
          </article>
        </div>
      </section>

      <section className="card">
        <div className="feature-grid">
          <div className="feature-card">
            <h3 style={{ color: 'var(--primary)' }}>Adaptive Questioning</h3>
            <p>AI generates tailored questions from the syllabus dynamically.</p>
          </div>
          <div className="feature-card">
            <h3 style={{ color: 'var(--secondary)' }}>Real-Time Tracking</h3>
            <p>Monitors correctness and confidence to identify misconceptions and weak areas.</p>
          </div>
          <div className="feature-card">
            <h3 style={{ color: 'var(--success)' }}>Detailed Analytics</h3>
            <p>Receive instant comprehensive reports and feedback after completion.</p>
          </div>
        </div>
      </section>
    </main>
  );
};

export default Landing;
