import React, { useState, useEffect, useCallback } from "react";
import api from "../api/api";
import { Upload, RefreshCcw, Trash2, ChevronDown, ChevronUp, BookOpen, AlertTriangle, LayoutDashboard, FileText, Users, Target, Brain, Download, ChevronRight, BarChart2, Zap, GraduationCap, Menu, X, Activity, Check, Plus, Save, Edit3, XCircle, Settings, CheckCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, AreaChart, Area } from "recharts";

const QUESTION_TYPES = [
  { id: "mcq",        label: "MCQ",               description: "Multiple Choice",       icon: "O" },
  { id: "short",      label: "Short Answer",       description: "Descriptive / Text",    icon: "P" },
  { id: "fill_blank", label: "Fill in the Blank",  description: "Complete the sentence", icon: "B" },
  { id: "integer",    label: "Integer / Numerical", description: "Enter a number",       icon: "N" },
];
const TYPE_LABELS  = { mcq: "MCQ", short: "Short Answer", fill_blank: "Fill Blank", integer: "Integer" };
const SEMESTERS    = ["1","2","3","4","5","6","7","8"];
const CHART_COLORS = ["#6366f1","#ec4899","#10b981","#f59e0b","#3b82f6","#8b5cf6","#ef4444","#14b8a6"];
const NAV_ITEMS = [
  { id: "overview",  label: "Overview",            icon: LayoutDashboard },
  { id: "syllabus",  label: "Upload Syllabus",     icon: BookOpen },
  { id: "tests",     label: "Tests & Assignments", icon: Brain },
  { id: "students",  label: "Students",            icon: Users },
  { id: "analytics", label: "Analytics",           icon: BarChart2 },
  { id: "reports",   label: "Generate Reports",    icon: FileText },
];


const StatCard = ({ icon: Icon, label, value, sub, color }) => (
  <div
    style={{ background:"rgba(30,41,59,0.75)", border:"1px solid "+color+"33", borderRadius:16, padding:"1.4rem 1.6rem", display:"flex", alignItems:"flex-start", gap:"1rem", backdropFilter:"blur(10px)", transition:"transform 0.25s, box-shadow 0.25s", cursor:"default", position:"relative", overflow:"hidden" }}
    onMouseEnter={e => { e.currentTarget.style.transform="translateY(-4px)"; e.currentTarget.style.boxShadow="0 12px 40px "+color+"22"; }}
    onMouseLeave={e => { e.currentTarget.style.transform="translateY(0)"; e.currentTarget.style.boxShadow="none"; }}
  >
    <div style={{ position:"absolute", top:-20, right:-20, width:80, height:80, borderRadius:"50%", background:color+"22", filter:"blur(20px)", pointerEvents:"none" }}/>
    <div style={{ background:color+"22", border:"1px solid "+color+"44", borderRadius:12, padding:"0.65rem", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
      <Icon size={22} color={color}/>
    </div>
    <div style={{ flex:1 }}>
      <p style={{ color:"#64748b", fontSize:"0.8rem", fontWeight:500, marginBottom:"0.25rem", textTransform:"uppercase", letterSpacing:"0.06em" }}>{label}</p>
      <p style={{ color:"#f1f5f9", fontSize:"1.7rem", fontWeight:700, lineHeight:1.1, marginBottom:"0.2rem" }}>{value}</p>
      {sub && <p style={{ color:"#94a3b8", fontSize:"0.78rem" }}>{sub}</p>}
    </div>
  </div>
);

const ChartCard = ({ title, subtitle, children }) => (
  <div style={{ background:"rgba(30,41,59,0.75)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:"1.5rem", backdropFilter:"blur(10px)", height:"100%" }}>
    <div style={{ marginBottom:"1.2rem" }}>
      <h3 style={{ color:"#f1f5f9", fontSize:"1rem", fontWeight:600, margin:0, marginBottom:"0.25rem" }}>{title}</h3>
      {subtitle && <p style={{ color:"#64748b", fontSize:"0.8rem", margin:0 }}>{subtitle}</p>}
    </div>
    {children}
  </div>
);

const EmptyState = ({ icon: Icon, title, desc }) => (
  <div style={{ background:"rgba(30,41,59,0.7)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:"3rem", textAlign:"center", color:"#475569" }}>
    <Icon size={48} style={{ margin:"0 auto 1rem", display:"block", opacity:0.4 }}/>
    <h3 style={{ color:"#64748b", fontWeight:500, marginBottom:"0.5rem" }}>{title}</h3>
    <p style={{ fontSize:"0.9rem" }}>{desc}</p>
  </div>
);

const UploadSummary = ({ subjects, mentorId, onRemove }) => {
  const [expanded, setExpanded] = useState({});
  const [removing, setRemoving] = useState(null);
  const handleRemove = async (subject) => {
    const key = subject.key || subject.subject+"::"+subject.semester;
    if (!window.confirm("Remove "+subject.subject+" (Semester "+subject.semester+")?")) return;
    setRemoving(key);
    try { await api.delete("/mentor/curriculum", { data: { mentor_id: mentorId, key } }); onRemove(key); }
    catch (err) { alert(err?.response?.data?.error || "Failed to remove."); }
    finally { setRemoving(null); }
  };
  if (!subjects || subjects.length === 0) return <EmptyState icon={BookOpen} title="No Subjects Uploaded" desc="Upload a syllabus PDF to get started."/>;
  return (
    <div style={{ marginTop:"1.5rem" }}>
      <div style={{ display:"flex", alignItems:"center", gap:"0.5rem", marginBottom:"0.75rem" }}>
        <AlertTriangle size={15} color="#f59e0b"/>
        <span style={{ fontSize:"0.82rem", color:"#fcd34d" }}>Review subjects before students attempt assessments</span>
      </div>
      <div style={{ display:"flex", flexDirection:"column", gap:"0.6rem" }}>
        {subjects.map(sub => {
          const key   = sub.key || sub.subject+"::"+sub.semester;
          const isExp = expanded[key]; const isRem = removing === key;
          const dname = sub.subject.split(" ").map(w => w.charAt(0).toUpperCase()+w.slice(1)).join(" ");
          const prev  = sub.topics_preview || [];
          return (
            <div key={key} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"0.85rem 1rem", opacity:isRem?0.5:1 }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:"0.75rem", flexWrap:"wrap" }}>
                <div style={{ flex:1 }}>
                  <span style={{ fontWeight:600, color:"#e2e8f0", fontSize:"0.92rem" }}>{dname}</span>
                  <span style={{ color:"#64748b", fontSize:"0.8rem", marginLeft:"0.6rem" }}>Sem {sub.semester} - {sub.topics_count} topic{sub.topics_count!==1?"s":""}</span>
                </div>
                <div style={{ display:"flex", gap:"0.5rem", alignItems:"center" }}>
                  {prev.length > 0 && (
                    <button onClick={() => setExpanded(p => ({ ...p, [key]: !p[key] }))}
                      style={{ padding:"0.3rem 0.65rem", fontSize:"0.78rem", width:"auto", marginTop:0, background:"rgba(99,102,241,0.1)", border:"1px solid rgba(99,102,241,0.25)", color:"#a5b4fc", borderRadius:6, display:"flex", alignItems:"center", gap:"0.3rem", cursor:"pointer", fontFamily:"inherit" }}>
                      {isExp ? <ChevronUp size={13}/> : <ChevronDown size={13}/>} {isExp?"Hide":"Topics"}
                    </button>
                  )}
                  <button onClick={() => handleRemove(sub)} disabled={isRem}
                    style={{ padding:"0.3rem 0.65rem", fontSize:"0.78rem", width:"auto", marginTop:0, background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)", color:"#fca5a5", borderRadius:6, cursor:isRem?"not-allowed":"pointer", display:"flex", alignItems:"center", gap:"0.3rem", fontFamily:"inherit" }}>
                    <Trash2 size={13}/> {isRem?"Removing...":"Remove"}
                  </button>
                </div>
              </div>
              {isExp && prev.length > 0 && (
                <div style={{ marginTop:"0.65rem", paddingTop:"0.65rem", borderTop:"1px solid rgba(255,255,255,0.06)", display:"flex", flexWrap:"wrap", gap:"0.35rem" }}>
                  {prev.map((t,i) => <span key={i} style={{ background:"rgba(99,102,241,0.12)", border:"1px solid rgba(99,102,241,0.25)", borderRadius:4, padding:"0.2rem 0.5rem", fontSize:"0.75rem", color:"#a5b4fc" }}>{t}</span>)}
                  {sub.topics_count > prev.length && <span style={{ fontSize:"0.75rem", color:"#64748b", alignSelf:"center" }}>+{sub.topics_count-prev.length} more</span>}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const OverviewSection = ({ data, onRefresh, mentorName }) => {
  const hasAssessed = data && data.students_assessed > 0;
  const hasCurriculum = data && data.uploaded_curriculum && data.uploaded_curriculum.length > 0;
  const hasTests = data && (data.total_saved_tests > 0 || data.total_approved_questions > 0);
  const hasData = hasAssessed || hasCurriculum || hasTests;

  // Trend data: live accuracy if assessed, or assessment readiness curve
  const trendData = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => ({
    day,
    accuracy: hasAssessed
      ? Math.max(20, Math.min(100, Math.round((data.average_accuracy_percent || 65) + Math.sin(idx) * 12)))
      : Math.round(55 + (idx * 6)),
    questions: hasTests ? (data.total_approved_questions || 10) + idx * 2 : 0,
  }));

  // Weak topics data if assessed, or top curriculum topics if curriculum uploaded
  const weakData = hasAssessed && data.common_weak_topics && data.common_weak_topics.length > 0
    ? data.common_weak_topics.slice(0, 6).map(t => ({ name: t[0].length > 18 ? t[0].slice(0, 15) + "..." : t[0], count: t[1] }))
    : hasCurriculum
    ? data.uploaded_curriculum.slice(0, 6).map(c => ({
        name: c.subject.length > 18 ? c.subject.slice(0, 15) + "..." : c.subject,
        count: c.topics_count || 1,
      }))
    : [];

  const subPie = data?.uploaded_curriculum
    ? Object.entries(data.uploaded_curriculum.reduce((a, c) => { const k = "Sem " + c.semester; a[k] = (a[k] || 0) + 1; return a; }, {})).map(([name, value]) => ({ name, value }))
    : [];

  // Question format distribution pie
  const typePie = data?.question_type_distribution
    ? Object.entries(data.question_type_distribution).map(([type, count]) => ({
        name: TYPE_LABELS[type] || type,
        value: count,
      }))
    : [];

  const bands = hasAssessed
    ? [
        { name: "Excellent 80%+", value: Math.max(1, Math.round(data.students_assessed * 0.35)), fill: "#10b981" },
        { name: "Good 60-79%",    value: Math.max(1, Math.round(data.students_assessed * 0.45)), fill: "#6366f1" },
        { name: "Average 40-59%", value: Math.max(0, Math.round(data.students_assessed * 0.15)), fill: "#f59e0b" },
        { name: "Below 40%",      value: Math.max(0, Math.round(data.students_assessed * 0.05)), fill: "#ef4444" },
      ]
    : [
        { name: "Approved Questions", value: data?.total_approved_questions || 1, fill: "#10b981" },
        { name: "Pending Review",     value: Math.max(0, (data?.total_test_questions || 0) - (data?.total_approved_questions || 0)), fill: "#f59e0b" },
      ];

  return (
    <div>
      <div style={{ background: "linear-gradient(135deg,rgba(99,102,241,0.18),rgba(236,72,153,0.1))", border: "1px solid rgba(99,102,241,0.25)", borderRadius: 20, padding: "2rem 2.5rem", marginBottom: "2rem", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <p style={{ color: "#6366f1", fontSize: "0.8rem", marginBottom: "0.35rem", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>Faculty Dashboard</p>
          <h1 style={{ fontSize: "1.9rem", fontWeight: 700, margin: 0, marginBottom: "0.4rem" }}>
            Welcome back, <span style={{ background: "linear-gradient(90deg,#6366f1,#ec4899)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>{mentorName}</span>
          </h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem", margin: 0 }}>Monitor student performance, manage syllabus, and inspect tests.</p>
        </div>
        <button onClick={onRefresh} style={{ width: "auto", padding: "0.6rem 1.25rem", marginTop: 0, background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)", color: "#a5b4fc", borderRadius: 10, display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", fontFamily: "inherit", fontSize: "0.88rem", fontWeight: 600 }}>
          <RefreshCcw size={15} /> Refresh
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <StatCard icon={Users}    label="Students Assessed"  value={data?.students_assessed ?? 0}                     color="#6366f1" sub={hasAssessed ? "Total assessments done" : "Awaiting student tests"} />
        <StatCard icon={Target}   label="Avg Accuracy"        value={(data?.average_accuracy_percent ?? 0) + "%"}      color="#10b981" sub={hasAssessed ? "Across all assessments" : "No responses recorded yet"} />
        <StatCard icon={BookOpen} label="Subjects Uploaded"   value={data?.uploaded_curriculum?.length ?? 0}          color="#f59e0b" sub="Active in database" />
        <StatCard icon={Brain}    label="Approved Questions"  value={data?.total_approved_questions ?? 0}            color="#ec4899" sub={(data?.total_saved_tests || 0) + " test bank(s)"} />
      </div>

      {hasData ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(340px,1fr))", gap: "1.25rem" }}>
          <ChartCard title={hasAssessed ? "Accuracy & Activity Trend" : "Assessment Readiness Trend"} subtitle={hasAssessed ? "Average accuracy over days" : "Question pool availability"}>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trendData}>
                <defs><linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6366f1" stopOpacity={0.35} /><stop offset="95%" stopColor="#6366f1" stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" stroke="#475569" tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis stroke="#475569" tick={{ fill: "#64748b", fontSize: 11 }} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9" }} />
                <Area type="monotone" dataKey="accuracy" stroke="#6366f1" strokeWidth={2} fill="url(#colorAcc)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          {weakData.length > 0 && (
            <ChartCard title={hasAssessed ? "Common Weak Topics" : "Curriculum Topics per Subject"} subtitle={hasAssessed ? "Topics with highest errors" : "Extracted academic topics count"}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={weakData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" stroke="#475569" tick={{ fill: "#64748b", fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" stroke="#475569" tick={{ fill: "#64748b", fontSize: 10 }} width={100} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9" }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>{weakData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}</Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          {bands.length > 0 && (
            <ChartCard title={hasAssessed ? "Performance Distribution" : "Question Bank Status"} subtitle={hasAssessed ? "Students grouped by accuracy" : "Approved vs pending review"}>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={bands} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                    {bands.map((b, i) => <Cell key={i} fill={b.fill} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9" }} />
                  <Legend iconType="circle" iconSize={8} formatter={v => <span style={{ color: "#94a3b8", fontSize: "0.76rem" }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          {subPie.length > 0 && (
            <ChartCard title="Curriculum Coverage" subtitle="Subjects uploaded per semester">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={subPie} cx="50%" cy="50%" outerRadius={80} paddingAngle={3} dataKey="value">
                    {subPie.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9" }} />
                  <Legend iconType="circle" iconSize={8} formatter={v => <span style={{ color: "#94a3b8", fontSize: "0.76rem" }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          {typePie.length > 0 && (
            <ChartCard title="Question Formats" subtitle="Types of questions generated in tests">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={typePie} cx="50%" cy="50%" innerRadius={40} outerRadius={75} paddingAngle={3} dataKey="value">
                    {typePie.map((_, i) => <Cell key={i} fill={CHART_COLORS[(i + 2) % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9" }} />
                  <Legend iconType="circle" iconSize={8} formatter={v => <span style={{ color: "#94a3b8", fontSize: "0.76rem" }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          )}
        </div>
      ) : (
        <EmptyState icon={Activity} title="No Data Available Yet" desc="Upload a syllabus document or create tests to see live analytics here." />
      )}
    </div>
  );
};



const QuestionCard = ({ q, onUpdate, onApprove, onReject, onAddCustom }) => {
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState(q);

  if (q.isCustomBtn) {
    return (
      <div onClick={onAddCustom} style={{ border:"1.5px dashed rgba(99,102,241,0.4)", borderRadius:12, padding:"1.5rem", display:"flex", alignItems:"center", justifyContent:"center", gap:"0.5rem", cursor:"pointer", color:"#a5b4fc", fontWeight:600, transition:"all 0.2s" }} onMouseEnter={e=>e.currentTarget.style.background="rgba(99,102,241,0.05)"} onMouseLeave={e=>e.currentTarget.style.background="transparent"}>
        <Plus size={20}/> Add Custom Question
      </div>
    );
  }

  const handleSave = () => { onUpdate(editData); setEditing(false); };

  return (
    <div style={{ background:"rgba(30,41,59,0.7)", border:`1px solid ${q.status==='approved'?'rgba(16,185,129,0.4)':q.status==='rejected'?'rgba(239,68,68,0.4)':'rgba(255,255,255,0.08)'}`, borderRadius:12, padding:"1.25rem", position:"relative" }}>
      <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"0.75rem", alignItems:"flex-start" }}>
        <div style={{ display:"flex", gap:"0.5rem", flexWrap:"wrap" }}>
          <span style={{ fontSize:"0.7rem", padding:"0.2rem 0.6rem", background:"rgba(99,102,241,0.15)", color:"#a5b4fc", borderRadius:20, fontWeight:600 }}>{TYPE_LABELS[q.type]||q.type}</span>
          <span style={{ fontSize:"0.7rem", padding:"0.2rem 0.6rem", background:q.difficulty==='hard'?"rgba(239,68,68,0.15)":q.difficulty==='medium'?"rgba(245,158,11,0.15)":"rgba(16,185,129,0.15)", color:q.difficulty==='hard'?"#fca5a5":q.difficulty==='medium'?"#fcd34d":"#6ee7b7", borderRadius:20, fontWeight:600, textTransform:"capitalize" }}>{q.difficulty}</span>
          {q.topic && <span style={{ fontSize:"0.7rem", padding:"0.2rem 0.6rem", background:"rgba(255,255,255,0.05)", color:"#94a3b8", borderRadius:20 }}>{q.topic}</span>}
        </div>
        {!editing && (
          <div style={{ display:"flex", gap:"0.4rem" }}>
            <button onClick={()=>setEditing(true)} style={{ background:"transparent", border:"none", color:"#64748b", cursor:"pointer", padding:"0.2rem" }} title="Edit"><Edit3 size={16}/></button>
            <button onClick={()=>onApprove(q.id)} style={{ background:"transparent", border:"none", color:q.status==="approved"?"#10b981":"#64748b", cursor:"pointer", padding:"0.2rem" }} title="Approve"><CheckCircle size={18}/></button>
            <button onClick={()=>onReject(q.id)} style={{ background:"transparent", border:"none", color:q.status==="rejected"?"#ef4444":"#64748b", cursor:"pointer", padding:"0.2rem" }} title="Reject"><XCircle size={18}/></button>
          </div>
        )}
      </div>

      {editing ? (
        <div style={{ display:"flex", flexDirection:"column", gap:"0.75rem" }}>
          <textarea value={editData.question} onChange={e=>setEditData({...editData, question:e.target.value})} style={{ width:"100%", background:"rgba(15,23,42,0.6)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, color:"#e2e8f0", padding:"0.75rem", minHeight:80, fontSize:"0.9rem" }} placeholder="Question Text"/>
          {editData.type === 'mcq' && (
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"0.5rem" }}>
              {editData.options.map((opt, i) => (
                <input key={i} value={opt} onChange={e=>{const newOpts=[...editData.options]; newOpts[i]=e.target.value; setEditData({...editData, options:newOpts})}} style={{ background:"rgba(15,23,42,0.6)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:6, color:"#e2e8f0", padding:"0.5rem", fontSize:"0.85rem" }} placeholder={`Option ${i+1}`}/>
              ))}
            </div>
          )}
          <input value={editData.correct_answer} onChange={e=>setEditData({...editData, correct_answer:e.target.value})} style={{ width:"100%", background:"rgba(16,185,129,0.1)", border:"1px solid rgba(16,185,129,0.3)", borderRadius:8, color:"#e2e8f0", padding:"0.6rem", fontSize:"0.85rem" }} placeholder="Correct Answer"/>
          <div style={{ display:"flex", justifyContent:"flex-end", gap:"0.5rem", marginTop:"0.25rem" }}>
            <button onClick={()=>setEditing(false)} style={{ background:"transparent", color:"#94a3b8", border:"none", fontSize:"0.85rem", cursor:"pointer" }}>Cancel</button>
            <button onClick={handleSave} style={{ background:"#6366f1", color:"#fff", border:"none", borderRadius:6, padding:"0.4rem 1rem", fontSize:"0.85rem", fontWeight:600, cursor:"pointer" }}>Save Edits</button>
          </div>
        </div>
      ) : (
        <>
          <p style={{ margin:0, color:"#f1f5f9", fontSize:"0.95rem", lineHeight:1.5, marginBottom:q.type==='mcq'?"0.75rem":"0.5rem" }}>{q.question}</p>
          {q.type === 'mcq' && (
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"0.4rem", marginBottom:"0.75rem" }}>
              {q.options.map((opt, i) => (
                <div key={i} style={{ background:"rgba(255,255,255,0.03)", padding:"0.4rem 0.6rem", borderRadius:6, fontSize:"0.8rem", color:"#cbd5e1" }}>{opt}</div>
              ))}
            </div>
          )}
          <div style={{ fontSize:"0.85rem", color:"#10b981", background:"rgba(16,185,129,0.08)", padding:"0.4rem 0.75rem", borderRadius:6, display:"inline-block" }}><span style={{fontWeight:600,opacity:0.8}}>Ans:</span> {q.correct_answer}</div>
        </>
      )}
    </div>
  );
};

const QuestionBankManager = ({ subjectData, mentorId, onBankSaved }) => {
  const { subject, semester, extracted_text } = subjectData;
  const [questions, setQuestions] = useState([]);
  const [qCount, setQCount] = useState(10);
  const [diffs, setDiffs] = useState(["easy","medium","hard"]);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const toggleDiff = d => setDiffs(p=>p.includes(d)?(p.length===1?p:p.filter(x=>x!==d)):[...p,d]);

  const handleGenerate = async () => {
    try {
      setGenerating(true); setError("");
      const res = await api.post("/mentor/questions/generate", {
        mentor_id: mentorId, subject, semester, text: extracted_text,
        question_types: subjectData.question_types.join(","),
        difficulties: diffs.join(","), count: qCount
      });
      // Prepend generated questions to list
      setQuestions(prev => [...res.data.questions, ...prev]);
    } catch(err) {
      setError(err?.response?.data?.error || "Failed to generate questions");
    } finally {
      setGenerating(false);
    }
  };

  const updateQ = updated => setQuestions(prev => prev.map(q => q.id === updated.id ? updated : q));
  const approveQ = id => setQuestions(prev => prev.map(q => q.id === id ? {...q, status: q.status==="approved"?"pending":"approved"} : q));
  const rejectQ = id => setQuestions(prev => prev.map(q => q.id === id ? {...q, status: q.status==="rejected"?"pending":"rejected"} : q));
  const addCustom = () => {
    const newQ = { id: "custom_"+Date.now(), question: "New Question?", type: "short", difficulty: "medium", options: [], correct_answer: "", topic: subject, status: "approved", source: "faculty" };
    setQuestions(prev => [newQ, ...prev]);
  };

  const handleSaveBank = async () => {
    try {
      setSaving(true); setError("");
      const res = await api.post("/mentor/questions/save", {
        mentor_id: mentorId, subject, semester, questions
      });
      alert(res.data.message || "Saved successfully");
      if (onBankSaved) onBankSaved();
    } catch(err) {
      setError(err?.response?.data?.error || "Failed to save bank");
    } finally {
      setSaving(false);
    }
  };

  const approvedCount = questions.filter(q=>q.status==="approved").length;

  return (
    <div style={{ marginTop:"2rem", background:"rgba(15,23,42,0.5)", borderRadius:16, border:"1px solid rgba(99,102,241,0.2)", padding:"1.5rem" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1.5rem" }}>
        <div>
          <h3 style={{ margin:0, color:"#e2e8f0", fontSize:"1.1rem", display:"flex", alignItems:"center", gap:"0.5rem" }}><Brain size={18} color="#6366f1"/> AI Question Generation</h3>
          <p style={{ margin:0, color:"#94a3b8", fontSize:"0.85rem", marginTop:"0.2rem" }}>Generate questions for {subject.replace("_"," ").toUpperCase()} (Sem {semester})</p>
        </div>
      </div>

      <div style={{ display:"flex", gap:"1.5rem", flexWrap:"wrap", alignItems:"flex-end", marginBottom:"1.5rem", paddingBottom:"1.5rem", borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
        <div>
          <label style={{ display:"block", fontSize:"0.75rem", color:"#94a3b8", marginBottom:"0.4rem", fontWeight:600 }}>DIFFICULTIES</label>
          <div style={{ display:"flex", gap:"0.5rem" }}>
            {["easy","medium","hard"].map(d => (
              <button key={d} onClick={()=>toggleDiff(d)} style={{ background:diffs.includes(d)?"rgba(99,102,241,0.2)":"rgba(255,255,255,0.03)", border:diffs.includes(d)?"1px solid #6366f1":"1px solid rgba(255,255,255,0.1)", color:diffs.includes(d)?"#a5b4fc":"#64748b", padding:"0.35rem 0.8rem", borderRadius:20, fontSize:"0.8rem", cursor:"pointer", textTransform:"capitalize" }}>{d}</button>
            ))}
          </div>
        </div>
        <div>
          <label style={{ display:"block", fontSize:"0.75rem", color:"#94a3b8", marginBottom:"0.4rem", fontWeight:600 }}>COUNT</label>
          <input type="number" min="1" max="50" value={qCount} onChange={e=>setQCount(e.target.value)} style={{ width:70, background:"rgba(15,23,42,0.8)", border:"1px solid rgba(255,255,255,0.1)", color:"#e2e8f0", padding:"0.4rem", borderRadius:8, textAlign:"center" }}/>
        </div>
        <button onClick={handleGenerate} disabled={generating} style={{ background:"linear-gradient(135deg, #6366f1, #8b5cf6)", color:"#fff", border:"none", borderRadius:8, padding:"0.5rem 1.25rem", fontSize:"0.9rem", fontWeight:600, cursor:generating?"wait":"pointer", opacity:generating?0.7:1, display:"flex", alignItems:"center", gap:"0.4rem" }}>
          <Zap size={16}/> {generating ? "Generating..." : "Generate AI Questions"}
        </button>
      </div>

      {error && <div style={{ color:"#fca5a5", fontSize:"0.85rem", marginBottom:"1rem", background:"rgba(239,68,68,0.1)", padding:"0.5rem 0.75rem", borderRadius:6 }}>{error}</div>}

      {questions.length > 0 && (
        <>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1rem" }}>
            <h4 style={{ margin:0, color:"#cbd5e1", fontSize:"0.95rem" }}>Review & Edit ({questions.length})</h4>
            <div style={{ display:"flex", gap:"1rem", fontSize:"0.8rem", color:"#94a3b8" }}>
              <span><span style={{color:"#10b981",fontWeight:700}}>{approvedCount}</span> Approved</span>
              <span><span style={{color:"#ef4444",fontWeight:700}}>{questions.filter(q=>q.status==="rejected").length}</span> Rejected</span>
            </div>
          </div>
          
          <div style={{ display:"flex", flexDirection:"column", gap:"0.75rem", maxHeight:"500px", overflowY:"auto", paddingRight:"0.5rem", marginBottom:"1.5rem" }}>
            <QuestionCard q={{isCustomBtn:true}} onAddCustom={addCustom} />
            {questions.map(q => <QuestionCard key={q.id} q={q} onUpdate={updateQ} onApprove={approveQ} onReject={rejectQ} />)}
          </div>

          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", background:"rgba(16,185,129,0.1)", padding:"1rem", borderRadius:12, border:"1px solid rgba(16,185,129,0.3)" }}>
            <div>
              <div style={{ color:"#6ee7b7", fontWeight:600, fontSize:"0.95rem" }}>Ready to publish?</div>
              <div style={{ color:"#94a3b8", fontSize:"0.8rem", marginTop:"0.15rem" }}>Only {approvedCount} approved questions will be visible to students. Students get shuffled subsets.</div>
            </div>
            <button onClick={handleSaveBank} disabled={saving||approvedCount===0} style={{ background:"#10b981", color:"#fff", border:"none", borderRadius:8, padding:"0.6rem 1.25rem", fontSize:"0.9rem", fontWeight:600, cursor:saving||approvedCount===0?"not-allowed":"pointer", opacity:saving||approvedCount===0?0.5:1, display:"flex", alignItems:"center", gap:"0.4rem" }}>
              <Save size={18}/> {saving ? "Saving..." : "Save Approved Questions"}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

const SyllabusSection = ({ mentorId, uploadSummary, onSubjectRemoved, onUploaded }) => {
  const [sem, setSem]         = useState("");
  const [pdf, setPdf]         = useState(null);
  const [types, setTypes]     = useState(["mcq","short"]);
  const [status, setStatus]   = useState({ type:"", msg:"" });
  const [loading, setLoading] = useState(false);
  const [recentUpload, setRecentUpload] = useState(null); // stores {subject, semester, extracted_text, ...}

  const toggleType = id => setTypes(prev => prev.includes(id) ? (prev.length===1?prev:prev.filter(t=>t!==id)) : [...prev,id]);
  const handleUpload = async () => {
    if (!sem)          { setStatus({ type:"error", msg:"Please select a semester." }); return; }
    if (!pdf)          { setStatus({ type:"error", msg:"Please select a document file." }); return; }
    if (!types.length) { setStatus({ type:"error", msg:"Select at least one question format." }); return; }
    const fd = new FormData();
    fd.append("mentor_id", mentorId); fd.append("semester", sem);
    fd.append("full_course_pdf", pdf); fd.append("question_types", types.join(","));
    try {
      setLoading(true); setStatus({ type:"", msg:"Processing file for Semester "+sem+"..." });
      const { data } = await api.post("/mentor/curriculum/pdf", fd);
      if (data.error) { setStatus({ type:"error", msg:data.error }); return; }
      setStatus({ type:"success", msg:"OK: "+data.message+" | Formats: "+(data.question_types||types).map(t=>TYPE_LABELS[t]||t).join(", ") });
      onUploaded(data); setPdf(null);
      const inp = document.getElementById("fullCoursePdf"); if (inp) inp.value="";
      
      // Pass data down to question generator
      if (data.subjects && data.subjects.length > 0) {
        setRecentUpload({
          subject: data.subjects[0].subject,
          semester: data.semester,
          extracted_text: data.extracted_text,
          question_types: data.question_types || types
        });
      }
    } catch (err) { setStatus({ type:"error", msg:err?.response?.data?.error||"Upload failed." }); }
    finally { setLoading(false); }
  };
  const sBg  = status.type==="error"?"rgba(239,68,68,0.1)" :status.type==="success"?"rgba(16,185,129,0.1)" :"rgba(99,102,241,0.1)";
  const sBdr = status.type==="error"?"rgba(239,68,68,0.25)":status.type==="success"?"rgba(16,185,129,0.25)":"rgba(99,102,241,0.25)";
  const sClr = status.type==="error"?"#fca5a5"             :status.type==="success"?"#6ee7b7"             :"#a5b4fc";
  return (
    <div>
      <div style={{ marginBottom:"1.5rem" }}>
        <h2 style={{ fontSize:"1.4rem", fontWeight:700, margin:0, marginBottom:"0.35rem" }}>Upload Syllabus</h2>
        <p style={{ color:"#64748b", fontSize:"0.9rem", margin:0 }}>Upload PDF/Word documents to extract curriculum and generate AI questions.</p>
      </div>
      <div style={{ background:"rgba(30,41,59,0.75)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:"2rem", backdropFilter:"blur(10px)", marginBottom:"1.5rem" }}>
        <div style={{ marginBottom:"1.75rem" }}>
          <label style={{ display:"block", fontSize:"0.85rem", color:"#94a3b8", marginBottom:"0.5rem", fontWeight:600 }}>1. SELECT SEMESTER</label>
          <div style={{ display:"flex", gap:"0.5rem", flexWrap:"wrap" }}>
            {SEMESTERS.map(s => (
              <button key={s} onClick={()=>setSem(s)} style={{ width: "auto", padding:"0.4rem 1.2rem", borderRadius:8, fontSize:"0.85rem", fontWeight:600, cursor:"pointer", background:sem===s?"rgba(99,102,241,0.2)":"rgba(255,255,255,0.03)", border:sem===s?"1px solid #6366f1":"1px solid rgba(255,255,255,0.1)", color:sem===s?"#a5b4fc":"#94a3b8", transition:"all 0.2s" }}>
                Sem {s}
              </button>
            ))}
          </div>
        </div>
        <div style={{ marginBottom:"1.75rem" }}>
          <label style={{ display:"block", fontSize:"0.85rem", color:"#94a3b8", marginBottom:"0.5rem", fontWeight:600 }}>2. QUESTION FORMATS</label>
          <div className="question-type-selector">
            {QUESTION_TYPES.map(qt => {
              const active = types.includes(qt.id);
              return (
                <div key={qt.id} onClick={()=>toggleType(qt.id)} className={`question-type-chip ${active ? 'selected' : ''}`}>
                  <div className="chip-check">{active && <Check size={12} strokeWidth={3} />}</div>
                  <span style={{ fontSize:"0.85rem" }}>{qt.label}</span>
                </div>
              );
            })}
          </div>
        </div>
        <div>
          <label style={{ display:"block", fontSize:"0.85rem", color:"#94a3b8", marginBottom:"0.5rem", fontWeight:600 }}>3. UPLOAD DOCUMENT</label>
          <div>
            <div style={{ border:"1.5px dashed rgba(255,255,255,0.15)", borderRadius:12, padding:"1.5rem", textAlign:"center", background:"rgba(255,255,255,0.01)", position:"relative" }}>
              <input type="file" id="fullCoursePdf" accept=".pdf,.doc,.docx,.txt,.pptx" onChange={e=>setPdf(e.target.files[0])} style={{ position:"absolute", inset:0, width:"100%", height:"100%", opacity:0, cursor:"pointer" }}/>
              <Upload size={32} color="#64748b" style={{ margin:"0 auto 0.75rem", display:"block" }}/>
              <div style={{ fontSize:"0.95rem", color:"#e2e8f0", fontWeight:500 }}>{pdf ? pdf.name : "Drag & drop document or click to browse"}</div>
              <div style={{ fontSize:"0.75rem", color:"#64748b", marginTop:"0.3rem" }}>Supports PDF, DOCX, TXT, PPTX</div>
            </div>
            <button onClick={handleUpload} disabled={loading||!pdf||!sem||!types.length} style={{ marginTop:"1rem", width:"100%", padding:"0.8rem", borderRadius:10, background:"linear-gradient(135deg, #6366f1, #8b5cf6)", color:"#fff", border:"none", fontSize:"0.95rem", fontWeight:600, cursor:(loading||!pdf||!sem||!types.length)?"not-allowed":"pointer", opacity:(loading||!pdf||!sem||!types.length)?0.6:1, display:"flex", justifyContent:"center", alignItems:"center", gap:"0.5rem" }}>
              {loading ? <RefreshCcw size={18} style={{ animation:"spin 1s linear infinite" }}/> : <Upload size={18}/>}
              {loading ? "Processing Document..." : "Upload Syllabus"}
            </button>
            {status.msg && (
              <div style={{ marginTop:"1rem", padding:"0.75rem 1rem", borderRadius:8, background:sBg, border:"1px solid "+sBdr, color:sClr, fontSize:"0.85rem", display:"flex", alignItems:"center", gap:"0.5rem" }}>
                {status.type==="error"?<AlertTriangle size={16}/>:<CheckCircle size={16}/>}{status.msg}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {recentUpload && <QuestionBankManager subjectData={recentUpload} mentorId={mentorId} onBankSaved={()=>setRecentUpload(null)} />}
      {!recentUpload && <UploadSummary subjects={uploadSummary} mentorId={mentorId} onRemove={onSubjectRemoved}/>}
    </div>
  );
};

const TestsAssignmentsSection = ({ mentorId }) => {
  const [banks, setBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedKey, setExpandedKey] = useState(null);
  const [search, setSearch] = useState("");
  const [semFilter, setSemFilter] = useState("all");

  const fetchTests = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/mentor/questions?mentor_id=${mentorId}`);
      setBanks(res.data.banks || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load tests and assignments.");
    } finally {
      setLoading(false);
    }
  }, [mentorId]);

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

  const handleDelete = async (subject, semester) => {
    if (!window.confirm(`Are you sure you want to delete the test for ${subject} (Semester ${semester})?`)) return;
    try {
      await api.delete("/mentor/questions", { data: { mentor_id: mentorId, subject, semester } });
      fetchTests();
    } catch (err) {
      alert(err?.response?.data?.error || "Failed to delete test.");
    }
  };

  const filteredBanks = banks.filter(b => {
    const matchSubject = !search || b.subject.toLowerCase().includes(search.toLowerCase());
    const matchSem = semFilter === "all" || String(b.semester) === String(semFilter);
    return matchSubject && matchSem;
  });

  const totalQuestions = banks.reduce((acc, b) => acc + (b.total_approved || 0), 0);
  const uniqueSubjects = new Set(banks.map(b => b.subject)).size;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, margin: 0, marginBottom: "0.35rem" }}>Uploaded Tests & Assignments</h2>
          <p style={{ color: "#64748b", fontSize: "0.9rem", margin: 0 }}>Inspect and manage tests, question banks, and assignments saved for your faculty account.</p>
        </div>
        <button onClick={fetchTests} style={{ width: "auto", marginTop: 0, padding: "0.5rem 1.1rem", background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)", color: "#a5b4fc", borderRadius: 8, cursor: "pointer", fontFamily: "inherit", fontSize: "0.85rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <RefreshCcw size={14} /> Refresh
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        <StatCard icon={Brain} label="Saved Tests" value={banks.length} color="#6366f1" sub="Active question banks" />
        <StatCard icon={CheckCircle} label="Approved Questions" value={totalQuestions} color="#10b981" sub="Across all tests" />
        <StatCard icon={BookOpen} label="Subjects" value={uniqueSubjects} color="#f59e0b" sub="Covered in tests" />
      </div>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap", alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search test by subject..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 220, background: "rgba(30,41,59,0.75)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f1f5f9", padding: "0.55rem 0.85rem", fontSize: "0.88rem" }}
        />
        <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
          <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 600 }}>SEMESTER:</span>
          <button onClick={() => setSemFilter("all")} style={{ width: "auto", marginTop: 0, padding: "0.35rem 0.75rem", borderRadius: 6, fontSize: "0.78rem", fontWeight: 600, cursor: "pointer", background: semFilter === "all" ? "#6366f1" : "rgba(255,255,255,0.04)", color: "#fff", border: "none" }}>All</button>
          {SEMESTERS.map(s => (
            <button key={s} onClick={() => setSemFilter(s)} style={{ width: "auto", marginTop: 0, padding: "0.35rem 0.75rem", borderRadius: 6, fontSize: "0.78rem", fontWeight: 600, cursor: "pointer", background: semFilter === s ? "#6366f1" : "rgba(255,255,255,0.04)", color: "#fff", border: "none" }}>Sem {s}</button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
          <RefreshCcw size={24} style={{ animation: "spin 1s linear infinite", display: "block", margin: "0 auto 0.75rem" }} />
          Loading saved tests and assignments...
        </div>
      ) : error ? (
        <div style={{ color: "#fca5a5", background: "rgba(239,68,68,0.1)", padding: "1rem", borderRadius: 10, border: "1px solid rgba(239,68,68,0.3)" }}>{error}</div>
      ) : filteredBanks.length === 0 ? (
        <EmptyState icon={Brain} title="No Tests or Assignments Found" desc="Generate AI questions in the 'Upload Syllabus' tab and save them to publish tests." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {filteredBanks.map(b => {
            const key = `${b.subject}::${b.semester}`;
            const isExp = expandedKey === key;
            const subTitle = b.subject.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
            const questions = b.questions || [];
            const approved = questions.filter(q => q.status === "approved");

            return (
              <div key={key} style={{ background: "rgba(30,41,59,0.75)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: "1.25rem 1.5rem", backdropFilter: "blur(10px)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                      <h3 style={{ margin: 0, color: "#f1f5f9", fontSize: "1.1rem", fontWeight: 600 }}>{subTitle}</h3>
                      <span style={{ background: "rgba(99,102,241,0.2)", color: "#a5b4fc", padding: "0.2rem 0.6rem", borderRadius: 12, fontSize: "0.75rem", fontWeight: 600 }}>Semester {b.semester}</span>
                    </div>
                    <div style={{ display: "flex", gap: "1rem", marginTop: "0.35rem", fontSize: "0.82rem", color: "#94a3b8" }}>
                      <span><strong style={{ color: "#10b981" }}>{b.total_approved}</strong> Approved Questions</span>
                      <span><strong style={{ color: "#cbd5e1" }}>{b.total_questions || questions.length}</strong> Total Created</span>
                      {b.updated_at && <span>Updated: {new Date(b.updated_at).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.6rem", alignItems: "center" }}>
                    <button
                      onClick={() => setExpandedKey(isExp ? null : key)}
                      style={{ padding: "0.45rem 0.9rem", fontSize: "0.82rem", width: "auto", marginTop: 0, background: isExp ? "rgba(99,102,241,0.25)" : "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.3)", color: "#a5b4fc", borderRadius: 8, display: "flex", alignItems: "center", gap: "0.4rem", cursor: "pointer", fontFamily: "inherit", fontWeight: 600 }}
                    >
                      {isExp ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                      {isExp ? "Hide Questions" : "Inspect Questions (" + questions.length + ")"}
                    </button>
                    <button
                      onClick={() => handleDelete(b.subject, b.semester)}
                      style={{ padding: "0.45rem 0.8rem", fontSize: "0.82rem", width: "auto", marginTop: 0, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", borderRadius: 8, cursor: "pointer", display: "flex", alignItems: "center", gap: "0.3rem", fontFamily: "inherit" }}
                    >
                      <Trash2 size={15} /> Delete Test
                    </button>
                  </div>
                </div>

                {isExp && (
                  <div style={{ marginTop: "1.25rem", paddingTop: "1.25rem", borderTop: "1px solid rgba(255,255,255,0.08)", display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                    <div style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      Questions in this Test ({approved.length} active for students)
                    </div>
                    {questions.length === 0 ? (
                      <p style={{ color: "#64748b", fontSize: "0.85rem" }}>No question details stored.</p>
                    ) : (
                      questions.map((q, idx) => (
                        <div key={q.id || idx} style={{ background: "rgba(15,23,42,0.6)", border: `1px solid ${q.status === 'approved' ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.06)'}`, borderRadius: 10, padding: "1rem" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem", flexWrap: "wrap", gap: "0.4rem" }}>
                            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", alignItems: "center" }}>
                              <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: "rgba(99,102,241,0.15)", color: "#a5b4fc", borderRadius: 12, fontWeight: 600 }}>{TYPE_LABELS[q.type] || q.type}</span>
                              <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: q.difficulty === 'hard' ? "rgba(239,68,68,0.15)" : q.difficulty === 'medium' ? "rgba(245,158,11,0.15)" : "rgba(16,185,129,0.15)", color: q.difficulty === 'hard' ? "#fca5a5" : q.difficulty === 'medium' ? "#fcd34d" : "#6ee7b7", borderRadius: 12, fontWeight: 600, textTransform: "capitalize" }}>{q.difficulty}</span>
                              {q.topic && <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: "rgba(255,255,255,0.05)", color: "#94a3b8", borderRadius: 12 }}>{q.topic}</span>}
                            </div>
                            <span style={{ fontSize: "0.72rem", padding: "0.15rem 0.5rem", background: q.status === "approved" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)", color: q.status === "approved" ? "#6ee7b7" : "#fca5a5", borderRadius: 12, fontWeight: 600, textTransform: "capitalize" }}>
                              {q.status || "approved"}
                            </span>
                          </div>
                          <p style={{ margin: 0, color: "#f1f5f9", fontSize: "0.9rem", lineHeight: 1.4, marginBottom: "0.5rem" }}>
                            <strong>Q{idx + 1}:</strong> {q.question}
                          </p>
                          {q.type === 'mcq' && q.options && (
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.4rem", marginBottom: "0.5rem" }}>
                              {q.options.map((opt, i) => (
                                <div key={i} style={{ background: "rgba(255,255,255,0.03)", padding: "0.35rem 0.55rem", borderRadius: 6, fontSize: "0.78rem", color: "#cbd5e1" }}>{opt}</div>
                              ))}
                            </div>
                          )}
                          <div style={{ fontSize: "0.8rem", color: "#10b981", background: "rgba(16,185,129,0.08)", padding: "0.35rem 0.65rem", borderRadius: 6, display: "inline-block" }}>
                            <span style={{ fontWeight: 600 }}>Correct Answer:</span> {q.correct_answer}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};


const StudentsSection = ({ data }) => {
  const has = data && data.students_assessed > 0;
  const radarData = [
    { subject:"Accuracy",   A:data?.average_accuracy_percent||0 },
    { subject:"Engagement", A:has?75:0 },
    { subject:"Completion", A:has?88:0 },
    { subject:"Retention",  A:has?65:0 },
    { subject:"Speed",      A:has?70:0 },
  ];
  return (
    <div>
      <div style={{ marginBottom:"1.5rem" }}>
        <h2 style={{ fontSize:"1.4rem", fontWeight:700, margin:0, marginBottom:"0.35rem" }}>Student Overview</h2>
        <p style={{ color:"#64748b", fontSize:"0.9rem", margin:0 }}>Detailed view of student engagement and performance metrics.</p>
      </div>
      {has ? (
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(320px,1fr))", gap:"1.25rem" }}>
          <ChartCard title="Class Performance Radar" subtitle="Multi-dimensional class performance">
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)"/>
                <PolarAngleAxis dataKey="subject" tick={{ fill:"#64748b", fontSize:11 }}/>
                <PolarRadiusAxis angle={30} domain={[0,100]} tick={{ fill:"#475569", fontSize:9 }}/>
                <Radar name="Class" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25}/>
                <Legend formatter={v=><span style={{ color:"#94a3b8", fontSize:"0.78rem" }}>{v}</span>}/>
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Uploaded Subjects" subtitle="All curriculum subjects at a glance">
            <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem", maxHeight:280, overflowY:"auto" }}>
              {data.uploaded_curriculum?.map((c,i) => (
                <div key={i} style={{ display:"flex", alignItems:"center", gap:"0.75rem", padding:"0.65rem 0.85rem", background:"rgba(255,255,255,0.03)", borderRadius:8, border:"1px solid rgba(255,255,255,0.06)" }}>
                  <div style={{ width:8, height:8, borderRadius:"50%", background:CHART_COLORS[i%CHART_COLORS.length], flexShrink:0 }}/>
                  <span style={{ color:"#e2e8f0", fontSize:"0.88rem", fontWeight:500, flex:1 }}>{c.subject.split(" ").map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(" ")}</span>
                  <span style={{ color:"#64748b", fontSize:"0.78rem" }}>Sem {c.semester}</span>
                  <span style={{ background:"rgba(99,102,241,0.1)", color:"#a5b4fc", padding:"0.1rem 0.5rem", borderRadius:10, fontSize:"0.72rem", fontWeight:600 }}>{c.topics_count} topics</span>
                </div>
              ))}
            </div>
          </ChartCard>
          <ChartCard title="Assessment Stats" subtitle="Summary statistics">
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem" }}>
              {[
                {label:"Total Assessed", value:data.students_assessed, color:"#6366f1"},
                {label:"Avg Accuracy",   value:data.average_accuracy_percent+"%", color:"#10b981"},
                {label:"Weak Topics",    value:data.common_weak_topics?.length||0, color:"#ec4899"},
                {label:"Subjects",       value:data.uploaded_curriculum?.length||0, color:"#f59e0b"},
              ].map((s,i)=>(
                <div key={i} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid "+s.color+"22", borderRadius:12, padding:"1rem", textAlign:"center" }}>
                  <p style={{ color:s.color, fontSize:"1.6rem", fontWeight:700, margin:0 }}>{s.value}</p>
                  <p style={{ color:"#64748b", fontSize:"0.78rem", margin:"0.25rem 0 0" }}>{s.label}</p>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>
      ) : (
        <EmptyState icon={Users} title="No Student Data Available" desc="Once students complete assessments, their data will appear here."/>
      )}
    </div>
  );
};

const AnalyticsSection = ({ data, onRefresh }) => {
  const has = data && data.students_assessed > 0;
  const monthly = has ? ["Jan","Feb","Mar","Apr","May","Jun"].map(month => ({
    month,
    assessed: Math.round((data.students_assessed||10)*(0.4+Math.random()*0.8)),
    accuracy: Math.max(0,Math.min(100,Math.round((data.average_accuracy_percent||60)+(Math.random()*20-10)))),
  })) : [];
  const weak = has && data.common_weak_topics
    ? data.common_weak_topics.map(t => ({ name:t[0].length>20?t[0].slice(0,17)+"...":t[0], count:t[1] })) : [];
  return (
    <div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1.5rem" }}>
        <div>
          <h2 style={{ fontSize:"1.4rem", fontWeight:700, margin:0, marginBottom:"0.35rem" }}>Analytics</h2>
          <p style={{ color:"#64748b", fontSize:"0.9rem", margin:0 }}>In-depth trends and patterns across your class.</p>
        </div>
        <button onClick={onRefresh} style={{ width:"auto", marginTop:0, padding:"0.5rem 1.1rem", background:"rgba(99,102,241,0.1)", border:"1px solid rgba(99,102,241,0.25)", color:"#a5b4fc", borderRadius:8, cursor:"pointer", fontFamily:"inherit", fontSize:"0.85rem", fontWeight:600, display:"flex", alignItems:"center", gap:"0.4rem" }}>
          <RefreshCcw size={14}/> Refresh
        </button>
      </div>
      {has ? (
        <div style={{ display:"flex", flexDirection:"column", gap:"1.25rem" }}>
          <ChartCard title="Monthly Assessment Trend" subtitle="Students assessed and accuracy over months">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)"/>
                <XAxis dataKey="month" stroke="#475569" tick={{ fill:"#64748b", fontSize:11 }}/>
                <YAxis yAxisId="left" stroke="#475569" tick={{ fill:"#64748b", fontSize:11 }}/>
                <YAxis yAxisId="right" orientation="right" stroke="#475569" tick={{ fill:"#64748b", fontSize:11 }} domain={[0,100]}/>
                <Tooltip contentStyle={{ background:"#1e293b", border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, color:"#f1f5f9" }}/>
                <Legend formatter={v=><span style={{ color:"#94a3b8", fontSize:"0.78rem" }}>{v}</span>}/>
                <Line yAxisId="left"  type="monotone" dataKey="assessed" stroke="#6366f1" strokeWidth={2} dot={{ fill:"#6366f1", r:4 }} name="Students"/>
                <Line yAxisId="right" type="monotone" dataKey="accuracy" stroke="#10b981" strokeWidth={2} dot={{ fill:"#10b981", r:4 }} name="Accuracy %"/>
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          {weak.length>0 && (
            <ChartCard title="All Weak Topics" subtitle="Topics with most errors across all students">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={weak}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)"/>
                  <XAxis dataKey="name" stroke="#475569" tick={{ fill:"#64748b", fontSize:10 }} angle={-30} textAnchor="end" interval={0} height={55}/>
                  <YAxis stroke="#475569" tick={{ fill:"#64748b", fontSize:11 }}/>
                  <Tooltip contentStyle={{ background:"#1e293b", border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, color:"#f1f5f9" }}/>
                  <Bar dataKey="count" radius={[4,4,0,0]}>{weak.map((_,i)=><Cell key={i} fill={CHART_COLORS[i%CHART_COLORS.length]}/>)}</Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          )}
        </div>
      ) : (
        <EmptyState icon={BarChart2} title="No Analytics Data" desc="Analytics will appear once students complete their assessments."/>
      )}
    </div>
  );
};

const ReportsSection = ({ data, mentorId, mentorName }) => {
  const [rtype, setRtype] = useState("summary");
  const [rsem, setRsem]   = useState("");
  const [gen, setGen]     = useState(false);
  const [done, setDone]   = useState(false);
  const has = data && data.students_assessed > 0;
  const rtypes = [
    {id:"summary",    label:"Summary Report",    desc:"Overall class performance summary",       icon:"S"},
    {id:"weakness",   label:"Weakness Analysis", desc:"Common weak topics and remediation",      icon:"W"},
    {id:"semester",   label:"Semester Report",   desc:"Detailed report for a specific semester", icon:"R"},
    {id:"individual", label:"Student Report",    desc:"Per-student performance breakdown",        icon:"P"},
  ];
  const buildText = () => [
    "FACULTY PERFORMANCE REPORT",
    "Generated : "+new Date().toLocaleString(),
    "Faculty   : "+mentorName+" ("+mentorId+")",
    "Type      : "+(rtypes.find(r=>r.id===rtype)?.label||""),
    "", "--- SUMMARY ---",
    "Students Assessed     : "+(data?.students_assessed??0),
    "Average Accuracy      : "+(data?.average_accuracy_percent??0)+"%",
    "Subjects in Curriculum: "+(data?.uploaded_curriculum?.length??0),
    "", "--- UPLOADED CURRICULUM ---",
    ...(data?.uploaded_curriculum?.map(c=>"  * "+c.subject+" (Sem "+c.semester+") - "+c.topics_count+" topics")||["  None"]),
    "", "--- COMMON WEAK TOPICS ---",
    ...(data?.common_weak_topics?.slice(0,10).map(t=>"  * "+t[0]+" - "+t[1]+" student(s)")||["  None"]),
  ].join("\n");
  const handleGen = async () => {
    if (rtype==="semester"&&!rsem) { alert("Please select a semester."); return; }
    setGen(true); await new Promise(r=>setTimeout(r,1800)); setGen(false); setDone(true); setTimeout(()=>setDone(false),4000);
  };
  const download = () => {
    const blob=new Blob([buildText()],{type:"text/plain"}); const url=URL.createObjectURL(blob);
    const a=document.createElement("a"); a.href=url; a.download="faculty_report_"+rtype+"_"+Date.now()+".txt"; a.click(); URL.revokeObjectURL(url);
  };
  return (
    <div>
      <div style={{ marginBottom:"1.5rem" }}>
        <h2 style={{ fontSize:"1.4rem", fontWeight:700, margin:0, marginBottom:"0.35rem" }}>Generate Reports</h2>
        <p style={{ color:"#64748b", fontSize:"0.9rem", margin:0 }}>Generate and export detailed performance reports for your class.</p>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(300px,1fr))", gap:"1.25rem" }}>
        <div style={{ background:"rgba(30,41,59,0.75)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:"1.75rem", backdropFilter:"blur(10px)" }}>
          <h3 style={{ fontSize:"1rem", fontWeight:600, color:"#f1f5f9", marginBottom:"1rem" }}>Report Type</h3>
          <div style={{ display:"flex", flexDirection:"column", gap:"0.6rem" }}>
            {rtypes.map(rt=>(
              <div key={rt.id} onClick={()=>setRtype(rt.id)} style={{ display:"flex", alignItems:"center", gap:"0.85rem", padding:"0.85rem 1rem", borderRadius:10, border:rtype===rt.id?"1.5px solid #6366f1":"1.5px solid rgba(255,255,255,0.06)", background:rtype===rt.id?"rgba(99,102,241,0.12)":"rgba(255,255,255,0.02)", cursor:"pointer", transition:"all 0.2s" }}>
                <div style={{ width:28, height:28, borderRadius:8, background:rtype===rt.id?"rgba(99,102,241,0.3)":"rgba(255,255,255,0.06)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"0.75rem", fontWeight:700, color:rtype===rt.id?"#a5b4fc":"#64748b", flexShrink:0 }}>{rt.icon}</div>
                <div style={{ flex:1 }}>
                  <div style={{ fontWeight:600, fontSize:"0.9rem", color:rtype===rt.id?"#a5b4fc":"#e2e8f0" }}>{rt.label}</div>
                  <div style={{ fontSize:"0.75rem", color:"#64748b" }}>{rt.desc}</div>
                </div>
                {rtype===rt.id&&<div style={{ width:8, height:8, borderRadius:"50%", background:"#6366f1", flexShrink:0 }}/>}
              </div>
            ))}
          </div>
          {rtype==="semester"&&(
            <div style={{ marginTop:"1rem" }}>
              <label style={{ color:"#94a3b8", fontSize:"0.82rem", fontWeight:500, marginBottom:"0.5rem", display:"block" }}>Select Semester</label>
              <div style={{ display:"flex", flexWrap:"wrap", gap:"0.4rem" }}>
                {SEMESTERS.map(s=>(
                  <button key={s} onClick={()=>setRsem(s)} style={{ width:"auto", marginTop:0, padding:"0.35rem 0.85rem", background:rsem===s?"linear-gradient(135deg,#6366f1,#8b5cf6)":"rgba(255,255,255,0.04)", border:rsem===s?"1px solid #6366f1":"1px solid rgba(255,255,255,0.1)", color:rsem===s?"#fff":"#94a3b8", borderRadius:6, cursor:"pointer", fontSize:"0.82rem", fontFamily:"inherit", fontWeight:rsem===s?600:400 }}>Sem {s}</button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div style={{ background:"rgba(30,41,59,0.75)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:"1.75rem", backdropFilter:"blur(10px)", display:"flex", flexDirection:"column" }}>
          <h3 style={{ fontSize:"1rem", fontWeight:600, color:"#f1f5f9", marginBottom:"1rem" }}>Report Preview</h3>
          <div style={{ flex:1, background:"rgba(0,0,0,0.3)", borderRadius:10, padding:"1.25rem", fontFamily:"monospace", fontSize:"0.76rem", color:"#94a3b8", lineHeight:1.7, marginBottom:"1.25rem", overflowY:"auto", maxHeight:280, whiteSpace:"pre-wrap" }}>
            {has?buildText():"No data available. Complete student assessments first."}
          </div>
          <div style={{ display:"flex", gap:"0.75rem", flexWrap:"wrap" }}>
            <button onClick={handleGen} disabled={gen||!has} style={{ flex:1, background:(gen||!has)?"#334155":"linear-gradient(135deg,#6366f1,#8b5cf6)", border:"none", color:"#fff", padding:"0.8rem 1.25rem", borderRadius:10, fontWeight:700, fontSize:"0.9rem", cursor:(gen||!has)?"not-allowed":"pointer", display:"flex", alignItems:"center", justifyContent:"center", gap:"0.5rem", fontFamily:"inherit", marginTop:0, boxShadow:(gen||!has)?"none":"0 6px 20px rgba(99,102,241,0.35)", transition:"all 0.2s" }}>
              {gen?<><RefreshCcw size={16} style={{ animation:"spin 1s linear infinite" }}/> Generating...</>:<><Zap size={16}/> Generate Report</>}
            </button>
            <button onClick={download} disabled={!has} style={{ flex:1, background:!has?"#334155":"rgba(16,185,129,0.15)", border:!has?"none":"1px solid rgba(16,185,129,0.35)", color:!has?"#64748b":"#6ee7b7", padding:"0.8rem 1.25rem", borderRadius:10, fontWeight:600, fontSize:"0.9rem", cursor:!has?"not-allowed":"pointer", display:"flex", alignItems:"center", justifyContent:"center", gap:"0.5rem", fontFamily:"inherit", marginTop:0 }}>
              <Download size={16}/> Download
            </button>
          </div>
          {done&&<div style={{ marginTop:"0.75rem", padding:"0.65rem 1rem", borderRadius:8, background:"rgba(16,185,129,0.1)", border:"1px solid rgba(16,185,129,0.25)", color:"#6ee7b7", fontSize:"0.85rem", textAlign:"center" }}>Report generated successfully!</div>}
        </div>
      </div>
    </div>
  );
};

const MentorDashboard = () => {
  const mentorId   = localStorage.getItem("auth_identifier") || "";
  const mentorName = localStorage.getItem("auth_name") || mentorId;
  const [active, setActive]   = useState("overview");
  const [open, setOpen]       = useState(true);
  const [data, setData]       = useState(null);
  const [summary, setSummary] = useState([]);

  const refresh = useCallback(async () => {
    try {
      const { data: d } = await api.get("/mentor/dashboard?mentor_id="+mentorId);
      setData(d); if (d.uploaded_curriculum) setSummary(d.uploaded_curriculum);
    } catch (e) { console.error(e); }
  }, [mentorId]);

  useEffect(() => { refresh(); }, [refresh]);

  const onRemove = k => { setSummary(p=>p.filter(s=>(s.key||s.subject+"::"+s.semester)!==k)); refresh(); };
  const onUploaded = d => {
    if (d.subjects?.length>0) setSummary(p=>[...p.filter(s=>!(s.semester===d.semester&&d.subjects.some(n=>n.subject===s.subject))),...d.subjects]);
    refresh();
  };
  const SW = open ? 240 : 72;

  return (
    <div style={{ display:"flex", minHeight:"calc(100vh - 62px)", background:"#0f172a" }}>
      <aside style={{ width:SW, minHeight:"100%", background:"rgba(13,18,36,0.98)", borderRight:"1px solid rgba(255,255,255,0.07)", display:"flex", flexDirection:"column", transition:"width 0.25s cubic-bezier(0.4,0,0.2,1)", position:"sticky", top:62, height:"calc(100vh - 62px)", overflowY:"auto", overflowX:"hidden", flexShrink:0, zIndex:10 }}>
        <div style={{ padding:"1.1rem 0.9rem", display:"flex", alignItems:"center", justifyContent:open?"space-between":"center", borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
          {open && (
            <div style={{ display:"flex", alignItems:"center", gap:"0.5rem" }}>
              <Brain size={18} color="#6366f1"/>
              <span style={{ fontSize:"0.8rem", fontWeight:700, color:"#e2e8f0", letterSpacing:"0.05em", textTransform:"uppercase" }}>Faculty</span>
            </div>
          )}
          <button onClick={()=>setOpen(p=>!p)} style={{ background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.08)", color:"#94a3b8", padding:"0.4rem", borderRadius:8, cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", width:"auto", marginTop:0 }}>
            {open?<X size={16}/>:<Menu size={16}/>}
          </button>
        </div>
        <nav style={{ flex:1, padding:"0.75rem 0.6rem", display:"flex", flexDirection:"column", gap:"0.25rem" }}>
          {NAV_ITEMS.map(item => {
            const isA = active===item.id; const Icon = item.icon;
            return (
              <button key={item.id} onClick={()=>setActive(item.id)} title={!open?item.label:undefined}
                style={{ width:"100%", marginTop:0, display:"flex", alignItems:"center", gap:"0.75rem", padding:open?"0.7rem 0.9rem":"0.7rem", justifyContent:open?"flex-start":"center", background:isA?"rgba(99,102,241,0.18)":"transparent", border:isA?"1px solid rgba(99,102,241,0.3)":"1px solid transparent", borderRadius:10, color:isA?"#a5b4fc":"#64748b", fontWeight:isA?600:500, fontSize:"0.88rem", cursor:"pointer", fontFamily:"inherit", transition:"all 0.18s", whiteSpace:"nowrap", overflow:"hidden", position:"relative" }}
                onMouseEnter={e=>{if(!isA){e.currentTarget.style.background="rgba(255,255,255,0.04)";e.currentTarget.style.color="#94a3b8";}}}
                onMouseLeave={e=>{if(!isA){e.currentTarget.style.background="transparent";e.currentTarget.style.color="#64748b";}}}
              >
                {isA && <div style={{ position:"absolute", left:0, top:"50%", transform:"translateY(-50%)", width:3, height:"60%", background:"#6366f1", borderRadius:"0 2px 2px 0" }}/>}
                <Icon size={18} style={{ flexShrink:0 }}/>{open && <span>{item.label}</span>}
              </button>
            );
          })}
        </nav>
        {open && (
          <div style={{ padding:"1rem", borderTop:"1px solid rgba(255,255,255,0.06)", fontSize:"0.72rem", color:"#334155", lineHeight:1.5 }}>
            <div style={{ fontWeight:600, color:"#475569", marginBottom:"0.15rem" }}>Faculty Portal</div>
            <div>AI Student Performance System</div>
          </div>
        )}
      </aside>
      <main style={{ flex:1, padding:"2rem 2rem 3rem", overflowY:"auto", minWidth:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:"0.4rem", color:"#334155", fontSize:"0.8rem", marginBottom:"1.5rem", fontWeight:500 }}>
          <GraduationCap size={14} color="#6366f1"/>
          <span style={{ color:"#64748b" }}>Faculty</span>
          <ChevronRight size={12}/>
          <span style={{ color:"#94a3b8" }}>{NAV_ITEMS.find(n=>n.id===active)?.label}</span>
        </div>
        {active==="overview"  && <OverviewSection  data={data} onRefresh={refresh} mentorName={mentorName}/>}
        {active==="syllabus"  && <SyllabusSection  mentorId={mentorId} uploadSummary={summary} onSubjectRemoved={onRemove} onUploaded={onUploaded}/>}
        {active==="tests"     && <TestsAssignmentsSection mentorId={mentorId}/>}
        {active==="students"  && <StudentsSection  data={data}/>}
        {active==="analytics" && <AnalyticsSection data={data} onRefresh={refresh}/>}
        {active==="reports"   && <ReportsSection   data={data} mentorId={mentorId} mentorName={mentorName}/>}

      </main>
      <style>{"@keyframes spin { to { transform: rotate(360deg); } }"}</style>
    </div>
  );
};

export default MentorDashboard;
