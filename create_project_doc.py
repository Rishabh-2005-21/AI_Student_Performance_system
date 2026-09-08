import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Styles & Colors
    NAVY = RGBColor(26, 54, 93)      # #1A365D Primary
    TEAL = RGBColor(13, 148, 136)    # #0D9488 Secondary
    CHARCOAL = RGBColor(45, 55, 72)  # #2D3748 Body text
    MUTED = RGBColor(113, 128, 150)  # #718096 Subtitle/Meta
    
    HEX_NAVY = "1A365D"
    HEX_TEAL = "0D9488"
    HEX_LIGHT_BG = "F7FAFC"
    HEX_BORDER = "CBD5E0"
    HEX_ALT_ROW = "EDF2F7"
    
    # Configure Default Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = CHARCOAL
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper Functions
    def add_title(text, subtitle_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = NAVY
        
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(18)
        run2 = p2.add_run(subtitle_text)
        run2.font.name = 'Calibri'
        run2.font.size = Pt(13)
        run2.font.italic = True
        run2.font.color.rgb = TEAL

    def add_meta_box(meta_dict):
        table = doc.add_table(rows=len(meta_dict), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_borders(table, color=HEX_BORDER, sz="4")
        
        for i, (k, v) in enumerate(meta_dict.items()):
            row = table.rows[i]
            cell_k = row.cells[0]
            cell_v = row.cells[1]
            cell_k.width = Inches(2.2)
            cell_v.width = Inches(4.3)
            
            set_cell_background(cell_k, "EDF2F7")
            set_cell_background(cell_v, HEX_LIGHT_BG)
            set_cell_margins(cell_k, top=80, bottom=80, left=120, right=120)
            set_cell_margins(cell_v, top=80, bottom=80, left=120, right=120)
            
            pk = cell_k.paragraphs[0]
            pk.paragraph_format.space_after = Pt(0)
            rk = pk.add_run(k)
            rk.font.bold = True
            rk.font.size = Pt(10)
            rk.font.color.rgb = NAVY
            
            pv = cell_v.paragraphs[0]
            pv.paragraph_format.space_after = Pt(0)
            rv = pv.add_run(v)
            rv.font.size = Pt(10)
            rv.font.color.rgb = CHARCOAL
            
        doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = NAVY
        
        # Add a subtle bottom border line via XML
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{HEX_TEAL}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = TEAL

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = NAVY

    def add_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        if bold_prefix:
            r_prefix = p.add_run(bold_prefix)
            r_prefix.font.bold = True
            r_prefix.font.color.rgb = NAVY
        r_text = p.add_run(text)
        r_text.font.color.rgb = CHARCOAL
        return p

    def add_bullet(text, bold_prefix=None, level=0):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        if bold_prefix:
            r_prefix = p.add_run(bold_prefix)
            r_prefix.font.bold = True
            r_prefix.font.color.rgb = NAVY
        r_text = p.add_run(text)
        r_text.font.color.rgb = CHARCOAL
        return p

    def add_callout(text, title="KEY INSIGHT", border_color=HEX_TEAL, bg_color=HEX_LIGHT_BG):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        r_title = p.add_run(f"[{title}]\n")
        r_title.font.bold = True
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = TEAL if border_color == HEX_TEAL else NAVY
        
        r_text = p.add_run(text)
        r_text.font.size = Pt(10)
        r_text.font.italic = True
        r_text.font.color.rgb = CHARCOAL
        
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def set_cell_background(cell, hex_color):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color=HEX_BORDER, sz="4"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
                <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)

    def format_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_borders(table, color=HEX_BORDER, sz="4")
        
        # Header Row
        hdr_cells = table.rows[0].cells
        for j, h_text in enumerate(headers):
            hdr_cells[j].width = Inches(col_widths[j])
            set_cell_background(hdr_cells[j], HEX_NAVY)
            set_cell_margins(hdr_cells[j], top=100, bottom=100, left=120, right=120)
            p = hdr_cells[j].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(h_text)
            r.font.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)
            
        # Data Rows
        for i, row_data in enumerate(data):
            row_cells = table.add_row().cells
            bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
            for j, val in enumerate(row_data):
                row_cells[j].width = Inches(col_widths[j])
                set_cell_background(row_cells[j], bg)
                set_cell_margins(row_cells[j], top=80, bottom=80, left=120, right=120)
                p = row_cells[j].paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(str(val))
                r.font.size = Pt(9)
                r.font.color.rgb = CHARCOAL

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # DOCUMENT GENERATION CONTENT
    # -------------------------------------------------------------

    # Title & Metadata Banners
    add_title(
        "AI-Based Real-Time Student Academic Performance Monitoring System",
        "System Architecture, Literature Review, Requirements Specification & Project Implementation Plan"
    )

    add_meta_box({
        "Document Type": "Detailed Engineering & Project Management Specification (.docx)",
        "System Scope": "Real-Time Adaptive Assessment, NLP Subjective Grading, Metacognitive Diagnostic Matrix",
        "Target Audience": "Faculty Reviewers, Academic Administrators, Software Engineering Lead",
        "Author / Lead": "AI Student Performance Engineering Team",
        "Status / Version": "Final Approved Specification — Version 1.0",
        "Creation Date": "August 2026"
    })

    # Executive Summary
    add_h1("Executive Summary")
    add_p(
        "Traditional educational evaluation systems rely heavily on periodic, static written examinations and fixed multiple-choice assessments. While easy to administer, these traditional methods suffer from critical systemic flaws: they evaluate performance retroactively, fail to measure genuine conceptual comprehension, lack real-time feedback, and completely ignore the metacognitive state of the learner (such as confidence levels, overconfidence, and deep-seated misconceptions).",
        bold_prefix="Background & Problem Context: "
    )
    add_p(
        "This project proposes and specifies the AI-Based Real-Time Student Academic Performance Monitoring System—an intelligent, web-based platform that dynamically evaluates students in real time. The system combines Natural Language Processing (NLP) answer scoring, Computerized Adaptive Testing (CAT) principles, and a 2x2 Metacognitive Knowledge-Confidence Diagnostic Engine. By pairing response correctness with self-reported confidence (Low, Medium, High), the system pinpoints not just what a student knows or gets wrong, but whether incorrect answers stem from a lack of knowledge or dangerous overconfidence.",
        bold_prefix="Proposed Innovation: "
    )

    add_callout(
        "The primary objective of this document is to establish a comprehensive literature review comparing five benchmark educational systems, define the stakeholder/user ecosystem, detail functional and non-functional system requirements, and present an actionable 20-week project plan with Work Breakdown Structures, milestones, and risk mitigations.",
        title="DOCUMENT PURPOSE"
    )

    # SECTION 1: Literature Review & Comparative Analysis
    add_h1("1. Literature Review & Comparative Analysis")
    add_p(
        "To establish a rigorous theoretical and empirical foundation for the proposed system, five key research frameworks and existing educational evaluation systems were systematically reviewed and evaluated. The analysis highlights their underlying methodologies, key findings, inherent limitations, and how the proposed system synthesizes and expands upon these contributions."
    )

    # Paper 1
    add_h2("1.1 Computerized Adaptive Testing (CAT) & Item Response Theory (IRT)")
    add_bullet("Wainer, H., Dorans, N. J., Flaugher, R., Green, B. F., & Mislevy, R. J. (2000). Computerized Adaptive Testing: A Primer (2nd ed.). Lawrence Erlbaum Associates.", bold_prefix="Citation: ")
    add_bullet("Item Response Theory (IRT) with 3-Parameter Logistic (3PL) models to dynamically estimate latent student ability (\u03b8) during test administration. Questions are selected iteratively from a calibrated question bank to maximize item information at the current ability estimate.", bold_prefix="Core Methodology: ")
    add_bullet("CAT reduces required assessment length by 50% to 60% compared to traditional linear tests while maintaining equal or higher measurement precision.", bold_prefix="Key Findings: ")
    add_bullet("Focuses strictly on objective multiple-choice items; treats every response as binary (correct/incorrect) without evaluating subjective reasoning or metacognitive confidence.", bold_prefix="Limitations: ")

    # Paper 2
    add_h2("1.2 Automated Essay & Short-Answer Evaluation using NLP Transformers")
    add_bullet("Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL; & Ramesh, D., et al. (2022). Transformer-Based Automated Short Answer Grading in Higher Education. IEEE Transactions on Learning Technologies.", bold_prefix="Citation: ")
    add_bullet("Fine-tuned Sentence-BERT (SBERT) and OpenAI Large Language Model (LLM) embeddings to compute semantic cosine similarity between student subjective answers and faculty model answers.", bold_prefix="Core Methodology: ")
    add_bullet("Achieves a high correlation (r >= 0.88) with expert human markers, effectively overcoming the brittle keyword-matching limitations of legacy regex/string-matching grading systems.", bold_prefix="Key Findings: ")
    add_bullet("Operates as an isolated scoring tool without dynamic difficulty adjustment, session-based adaptive question flow, or metacognitive confidence integration.", bold_prefix="Limitations: ")

    # Paper 3
    add_h2("1.3 Confidence-Based Marking (CBM) & Metacognitive Assessment")
    add_bullet("Gardner-Medwin, A. R. (1995, 2013). Confidence-Based Marking: Towards deeper learning and authentic assessment. Higher Education Academy; & Hunt, D. (2003). Metacognitive Knowledge Calibration.", bold_prefix="Citation: ")
    add_bullet("Pairs objective responses with self-reported certainty levels (Low, Medium, High). Applies a non-linear scoring matrix that rewards confident correct responses while heavily penalizing confident wrong answers.", bold_prefix="Core Methodology: ")
    add_bullet("Significantly reduces lucky guessing, promotes active reflection, and exposes uncalibrated student overconfidence before high-stakes summative exams.", bold_prefix="Key Findings: ")
    add_bullet("Historically restricted to paper tests or static quiz engines; lacks AI/NLP integration for free-text answers and automated question generation.", bold_prefix="Limitations: ")

    # Paper 4
    add_h2("1.4 Bayesian Knowledge Tracing (BKT) & Deep Knowledge Tracing (DKT)")
    add_bullet("Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing modeling; & Piech, C., Bassen, J., Huang, J., et al. (2015). Deep Knowledge Tracing. NeurIPS.", bold_prefix="Citation: ")
    add_bullet("Uses Recurrent Neural Networks (LSTM/GRU architectures) to model student skill acquisition trajectories across sequential exercise attempts.", bold_prefix="Core Methodology: ")
    add_bullet("DKT outperforms traditional hidden Markov models (BKT) by capturing complex non-linear skill relationships and long-term dependency patterns.", bold_prefix="Key Findings: ")
    add_bullet("High computational overhead, acts as a 'black-box' with low interpretability for course instructors, and requires large historical datasets.", bold_prefix="Limitations: ")

    # Paper 5
    add_h2("1.5 Learning Analytics Dashboards (LAD) & Diagnostic Indicators")
    add_bullet("Tempelaar, D. T., Rienties, B., & Giesbers, B. (2015). In search of the most informative data for feedback: Diagnostic analytics in LMS. Computers in Human Behavior.", bold_prefix="Citation: ")
    add_bullet("Aggregates LMS telemetry (login frequency, video view counts, forum posts, submission timestamps) to build early warning dashboards.", bold_prefix="Core Methodology: ")
    add_bullet("Identifies at-risk students 3-4 weeks prior to midterms, allowing timely academic interventions.", bold_prefix="Key Findings: ")
    add_bullet("Measures behavioral engagement rather than actual cognitive mastery, knowledge depth, or conceptual overconfidence.", bold_prefix="Limitations: ")

    # Comparison Table
    add_h2("1.6 Comparative Analysis Matrix")
    add_p("The table below synthesizes the five baseline research domains against key technical dimensions and compares them directly with the proposed AI-Based Real-Time Student Academic Performance Monitoring System:")

    col_widths = [1.2, 0.9, 1.0, 0.8, 0.8, 0.9, 0.9]
    headers = ["System / Study", "Assessment", "Evaluation Tech", "Confidence", "Real-Time", "Diagnostic Depth", "Gap Addressed"]
    data = [
        ["1. CAT / IRT (Wainer et al.)", "Dynamic (Adaptive)", "Objective / Item-Response", "No", "Yes", "Latent Ability (\u03b8)", "Added NLP + Confidence"],
        ["2. AES Transformers (Devlin/Ramesh)", "Static", "AI/NLP Cosine Embeddings", "No", "No (Batch)", "Subjective Score", "Added Adaptive CAT + Metacognition"],
        ["3. CBM Systems (Gardner-Medwin)", "Static", "Rule-based scoring matrix", "Yes (3-tier)", "No", "Overconfidence / Guessing", "Added AI/NLP + Dynamic CAT"],
        ["4. DKT (Piech et al.)", "Sequential", "Deep LSTM / RNN", "No", "Moderate", "Knowledge State Vector", "Added Explainable 2x2 Matrix"],
        ["5. LMS Dashboards (Tempelaar)", "Passive Logs", "Statistical Aggregation", "No", "Yes", "Behavioral Engagement", "Added Direct Knowledge Testing"],
        ["PROPOSED SYSTEM", "Dynamic (Adaptive)", "Hybrid (Rule + NLP Transformer)", "Yes (Low/Med/High)", "Yes (< 2s)", "2x2 Metacognitive Matrix", "Unified End-to-End Solution"]
    ]
    format_table(doc.add_table(rows=1, cols=7), col_widths, headers, data)

    add_callout(
        "Research Synthesis & System Novelty: Unlike existing systems that isolate either adaptive testing (CAT), subjective grading (NLP), or confidence marking (CBM), the proposed system unifies all three paradigms into a single, cohesive, real-time evaluation engine. It introduces a 2x2 Diagnostic Matrix mapping correctness against confidence to distinguish true mastery from guessing and dangerous overconfidence.",
        title="NOVELTY STATEMENT"
    )

    # SECTION 2: Stakeholders and Target Users
    add_h1("2. Stakeholders and Target Users Analysis")
    add_p(
        "A comprehensive analysis was conducted to identify all internal and external stakeholders who interact with, manage, or derive value from the proposed system. Understanding their roles, pain points, and requirements is critical to system design and user adoption."
    )

    add_h2("2.1 Stakeholder Identification & Categorization")
    add_bullet("Students enrolled in technical and academic courses seeking real-time assessment, conceptual diagnostic feedback, and self-awareness.", bold_prefix="Primary User Group 1 — Students: ")
    add_bullet("Professors, lecturers, and teaching assistants responsible for syllabus management, question bank curation, and monitoring class performance.", bold_prefix="Primary User Group 2 — Faculty / Instructors: ")
    add_bullet("Deans and Department Chairs requiring high-level analytics on topic mastery, curriculum efficacy, and institutional learning outcomes.", bold_prefix="Secondary Stakeholder Group 1 — Academic Administrators: ")
    add_bullet("System administrators and database engineers managing user authentication, role-based access, infrastructure stability, and security logs.", bold_prefix="Secondary Stakeholder Group 2 — IT / System Administrators: ")

    add_h2("2.2 Comprehensive Persona Profiles & Value Proposition")
    
    col_widths_s = [1.2, 1.3, 1.3, 1.4, 1.3]
    headers_s = ["Stakeholder Group", "Key Objectives", "Current Pain Points", "System Interaction", "Primary Value Delivered"]
    data_s = [
        ["Students (Target Users)", "Improve subject mastery, identify knowledge gaps, prepare for exams", "Delayed exam feedback, zero insight into overconfidence, repetitive static tests", "Takes adaptive tests, inputs confidence ratings, views diagnostic report", "Immediate real-time feedback, metacognitive self-awareness, targeted remediation"],
        ["Faculty / Instructors", "Identify class-wide topic weaknesses, streamline short-answer evaluation", "Manual grading load, inability to detect student overconfidence or guessing", "Creates question banks, sets topic weightages, reviews class analytics", "Automated subjective grading, clear topic misconception heatmaps"],
        ["Department Heads / Admin", "Monitor overall academic progress, accredit curriculum quality", "Siloed exam scores, lack of actionable topic-level performance data", "Views department-level summary reports, exports compliance analytics", "Data-driven curriculum evaluation and institutional learning assurance"],
        ["IT System Admin", "Ensure system security, 99.9% uptime, data privacy compliance", "Fragmented databases, unencrypted student records, unauthorized access risks", "Manages user roles, monitors API health, manages database backups", "Robust Role-Based Access Control (RBAC), security audit logs, scalable architecture"]
    ]
    format_table(doc.add_table(rows=1, cols=5), col_widths_s, headers_s, data_s)

    add_h2("2.3 Role-Based Access Control (RBAC) Hierarchy")
    add_p("The system enforces strict multi-tenant Role-Based Access Control across three primary access levels:")
    add_bullet("Granted permissions to register, select active subject assessments, answer dynamic questions, select confidence levels (Low, Medium, High), and view personal historical performance reports.", bold_prefix="1. Student Role ('student'): ")
    add_bullet("Granted permissions to manage subjects and topics, populate question banks (MCQ, Short Answer, Fill-Blank, Integer), trigger AI evaluation models, inspect class-wide diagnostic matrices, and generate student cohort reports.", bold_prefix="2. Faculty Role ('faculty'): ")
    add_bullet("Granted full administrative privileges including user account management, system configuration, database backup execution, audit log inspection, and system metrics monitoring.", bold_prefix="3. Administrator Role ('admin'): ")

    # SECTION 3: Functional Requirements
    add_h1("3. Functional Requirements (FR) Specification")
    add_p(
        "Functional requirements define the core capabilities, operations, and services that the system must provide. Requirements are organized into eight functional modules, uniquely identified for traceability."
    )

    add_h2("3.1 Core Module Requirements")

    # Module 1
    add_h3("Module 1: User Authentication & Account Management")
    add_bullet("The system shall allow users to register and log in securely using email and password credentials, returning a signed JWT token upon successful authentication.", bold_prefix="FR-1.1: ")
    add_bullet("The system shall enforce role-based access control (Student, Faculty, Admin) and restrict API endpoints according to active JWT claims.", bold_prefix="FR-1.2: ")
    add_bullet("The system shall support secure password hashing using bcrypt with a salt factor of 12 and handle session expiration after 60 minutes of inactivity.", bold_prefix="FR-1.3: ")

    # Module 2
    add_h3("Module 2: Subject & Question Bank Management")
    add_bullet("Faculty shall be able to create, read, update, and delete (CRUD) subjects and underlying topic hierarchies.", bold_prefix="FR-2.1: ")
    add_bullet("Faculty shall be able to populate question banks with four supported item types: Multiple Choice (MCQ), Short Answer (Subjective), Fill-in-the-Blank, and Integer/Numerical.", bold_prefix="FR-2.2: ")
    add_bullet("Each question item must be tagged with a subject ID, topic ID, difficulty level (Easy, Medium, Hard), correct answer string, and optional faculty model answer.", bold_prefix="FR-2.3: ")

    # Module 3
    add_h3("Module 3: AI Dynamic Question Selection Engine")
    add_bullet("The system shall initialize an assessment session for a student based on selected subject and fetch questions dynamically.", bold_prefix="FR-3.1: ")
    add_bullet("The system shall adjust question difficulty dynamically: increasing difficulty to 'Hard' after consecutive correct responses, and de-escalating difficulty to 'Easy' after incorrect responses.", bold_prefix="FR-3.2: ")
    add_bullet("The selection engine shall prevent question repetition within the same active assessment session.", bold_prefix="FR-3.3: ")

    # Module 4
    add_h3("Module 4: Student Interactive Assessment Interface")
    add_bullet("The system shall render questions one at a time on an interactive, responsive user web interface.", bold_prefix="FR-4.1: ")
    add_bullet("For every question presented, the system shall force the student to select a Metacognitive Confidence Level: 'Low', 'Medium', or 'High' before allowing response submission.", bold_prefix="FR-4.2: ")
    add_bullet("The interface shall display a real-time assessment progress indicator and session timer.", bold_prefix="FR-4.3: ")

    # Module 5
    add_h3("Module 5: Automated Multi-Type Answer Evaluation Engine")
    add_bullet("For MCQ questions, the engine shall perform strict string normalization and direct equality matching.", bold_prefix="FR-5.1: ")
    add_bullet("For Fill-in-the-Blank items, the engine shall execute fuzzy string matching using SequenceMatcher with a strict correctness threshold >= 0.80.", bold_prefix="FR-5.2: ")
    add_bullet("For Integer items, the engine shall parse string inputs into integer types and execute exact numerical matching.", bold_prefix="FR-5.3: ")
    add_bullet("For Subjective Short Answer items, the engine shall call OpenAI GPT / BERT NLP models to compute semantic similarity against faculty model answers. If API is unavailable, it shall gracefully fallback to lexical similarity.", bold_prefix="FR-5.4: ")

    # Module 6
    add_h3("Module 6: Metacognitive 2x2 Diagnostic Matrix Engine")
    add_bullet("The system shall classify every response into one of four diagnostic knowledge categories: (1) Strong Knowledge [Correct + High Conf], (2) Underconfident [Correct + Low Conf], (3) Misconception [Wrong + High Conf], (4) Weak Understanding [Wrong + Low Conf].", bold_prefix="FR-6.1: ")
    add_bullet("The system shall compute a total weighted response score using the formula: Total Score = Accuracy Score (60/0) + Confidence Score (+20 to -15) + Difficulty Weight (Easy: 5, Medium: 10, Hard: 15).", bold_prefix="FR-6.2: ")
    add_bullet("The system shall apply a penalty (-15 points) for overconfidence (Wrong + High Confidence) to discourage blind guessing and highlight dangerous misconceptions.", bold_prefix="FR-6.3: ")

    # Module 7
    add_h3("Module 7: Analytics & Reporting Engine")
    add_bullet("The system shall generate immediate post-assessment diagnostic reports for students, showing overall score, topic-wise accuracy, and confidence calibration.", bold_prefix="FR-7.1: ")
    add_bullet("The system shall provide faculty with class-wide dashboard analytics, highlighting topic misconception heatmaps and identifying at-risk students.", bold_prefix="FR-7.2: ")

    # Module 8
    add_h3("Module 8: System Administration & Audit Logging")
    add_bullet("The system shall record all assessment transactions in relational MySQL and document MongoDB databases.", bold_prefix="FR-8.1: ")
    add_bullet("The system shall allow faculty and administrators to export assessment analytics reports in CSV and PDF formats.", bold_prefix="FR-8.2: ")

    # Use Cases
    add_h2("3.2 Detailed Use Case Specifications")

    add_h3("Use Case 1: Student Takes Adaptive Assessment with Confidence Rating")
    add_bullet("Student logs into platform, selects 'Data Structures' subject, and clicks 'Start Assessment'.", bold_prefix="Primary Actor & Trigger: ")
    add_bullet("1. System fetches initial Medium difficulty question.\n2. System renders question text and confidence radio buttons (Low, Medium, High).\n3. Student enters answer and selects 'High' confidence.\n4. System submits payload to `/api/assessment/submit` endpoint.\n5. Evaluation engine scores answer, updates student model, selects next hard question.\n6. System presents next question until 10 questions are completed.\n7. System renders final diagnostic summary.", bold_prefix="Main Success Scenario: ")
    add_bullet("If student loses network connection, local storage buffers responses and syncs upon reconnection.", bold_prefix="Extensions / Exceptions: ")

    add_h3("Use Case 2: AI Evaluation Engine Scores Subjective Short Answer")
    add_bullet("Assessment Submission Service receives subjective text response.", bold_prefix="Primary Actor & Trigger: ")
    add_bullet("1. System normalizes student text and retrieves model answer from DB.\n2. System invokes AI Engine `evaluate_subjective()` function.\n3. AI Engine calculates semantic embedding cosine similarity score (e.g., 0.85).\n4. System compares score against threshold (0.60) -> Marks as Correct.\n5. System evaluates confidence ('Low') -> Assigns category 'Underconfident'.\n6. System stores response record and returns immediate feedback.", bold_prefix="Main Success Scenario: ")

    # SECTION 4: Non-Functional Requirements
    add_h1("4. Non-Functional Requirements (NFR) Specification")
    add_p(
        "Non-functional requirements define the quality attributes, performance benchmarks, security constraints, and operational standards that the system must satisfy."
    )

    col_widths_n = [1.3, 1.6, 2.3, 1.3]
    headers_n = ["Requirement ID", "Quality Attribute", "Quantitative Metric / Specification", "Verification Method"]
    data_n = [
        ["NFR-1.1", "Objective Latency", "Objective evaluation response time < 500 ms for 99% of requests", "Automated Load Testing (JMeter)"],
        ["NFR-1.2", "NLP Evaluation Latency", "AI/NLP subjective evaluation response time < 2.0 seconds", "API Latency Profiling"],
        ["NFR-1.3", "Concurrent Load", "Support up to 500 concurrent active test-taking sessions without performance degradation", "Stress Testing"],
        ["NFR-2.1", "Availability", "99.9% operational uptime during academic semester hours", "Uptime Monitoring (Prometheus)"],
        ["NFR-2.2", "Scalability", "Horizontal auto-scaling of backend containers when CPU load exceeds 70%", "Kubernetes Auto-Scaler Test"],
        ["NFR-3.1", "Data Encryption", "All data in transit encrypted via TLS 1.3; sensitive data at rest encrypted via AES-256", "Security Vulnerability Scan"],
        ["NFR-3.2", "Authentication", "JWT tokens signed using SHA-256 with 60-minute expiration; bcrypt password hashing (salt 12)", "Penetration Testing"],
        ["NFR-3.3", "Regulatory Compliance", "Full compliance with FERPA (student privacy) and GDPR guidelines", "Legal & Compliance Audit"],
        ["NFR-4.1", "Accessibility", "UI fully compliant with WCAG 2.1 Level AA standards (screen reader, high contrast)", "Axe Accessibility Audit"],
        ["NFR-4.2", "Usability", "Zero-friction interface; confidence selection achievable in single click", "User Usability Testing"],
        ["NFR-5.1", "Maintainability", "Modular REST architecture; PEP-8 compliant Python backend; ESLint compliant React code", "Static Code Analysis (SonarQube)"],
        ["NFR-6.1", "Fault Tolerance", "Graceful fallback to local SequenceMatcher if OpenAI API times out (> 3s)", "Automated Chaos Testing"],
        ["NFR-7.1", "NLP Scoring Accuracy", "Semantic similarity score correlation with human expert markers r >= 0.85", "Empirical Evaluation Benchmark"]
    ]
    format_table(doc.add_table(rows=1, cols=4), col_widths_n, headers_n, data_n)

    # SECTION 5: Comprehensive Project Plan
    add_h1("5. Comprehensive Project Implementation Plan")
    add_p(
        "The project execution is structured following an Agile Scrum framework spanning 20 calendar weeks (10 two-week sprints). This approach ensures iterative delivery, continuous validation, and structured milestone sign-offs."
    )

    add_h2("5.1 Work Breakdown Structure (WBS)")
    add_bullet("Feasibility study, detailed lit review, stakeholder interviews, architecture design, repository setup.", bold_prefix="Phase 1 (Weeks 1-2) — Requirement Engineering & Architecture: ")
    add_bullet("MySQL schema initialization, MongoDB collection design, Flask REST API framework, JWT auth integration.", bold_prefix="Phase 2 (Weeks 3-4) — Core Backend & Database Infrastructure: ")
    add_bullet("Faculty dashboard UI, subject/topic CRUD endpoints, question bank management with difficulty tags.", bold_prefix="Phase 3 (Weeks 5-6) — Syllabus & Question Bank Engine: ")
    add_bullet("CAT dynamic question selection algorithm, OpenAI GPT/BERT evaluation integration, fuzzy fallback engine.", bold_prefix="Phase 4 (Weeks 7-10) — AI NLP & Adaptive Testing Engine: ")
    add_bullet("Interactive student web UI, question rendering, metacognitive confidence selector component.", bold_prefix="Phase 5 (Weeks 11-12) — Student Interface & Confidence Module: ")
    add_bullet("2x2 matrix classification engine, weighted scoring logic, student diagnostic view, faculty heatmap.", bold_prefix="Phase 6 (Weeks 13-15) — Diagnostic Matrix & Analytics Dashboard: ")
    add_bullet("End-to-end integration, performance optimization, penetration testing, User Acceptance Testing (UAT).", bold_prefix="Phase 7 (Weeks 16-18) — Integration, Security & UAT: ")
    add_bullet("Production cloud deployment (Docker/AWS), user documentation sign-off, system training sessions.", bold_prefix="Phase 8 (Weeks 19-20) — Deployment, Training & Project Handover: ")

    add_h2("5.2 Major Project Milestones & Deliverables Schedule")

    col_widths_m = [0.8, 1.5, 2.5, 0.9, 0.8]
    headers_m = ["Milestone ID", "Milestone Name", "Key Deliverables & Verification Criteria", "Target Week", "Status"]
    data_m = [
        ["MS-1", "Architecture & Plan Approval", "SRS Document, Database ERD, Signed Architecture Design", "Week 2", "Approved"],
        ["MS-2", "Database & Auth Baseline", "Working MySQL DB, JWT Registration & Login APIs operational", "Week 4", "Completed"],
        ["MS-3", "Question Bank Module", "Faculty CRUD UI for MCQ, Short Answer, Fill-Blank, Integer items", "Week 6", "Completed"],
        ["MS-4", "AI Evaluation Core", "OpenAI/BERT evaluation pipeline with SequenceMatcher fallback verified", "Week 10", "Completed"],
        ["MS-5", "Student Test UI Complete", "Responsive test player with mandatory confidence selector UI", "Week 12", "Completed"],
        ["MS-6", "Diagnostic Matrix & Heatmap", "Real-time 2x2 matrix calculation and faculty class heatmap rendering", "Week 15", "Completed"],
        ["MS-7", "UAT & Security Sign-Off", "UAT completion with 95%+ pass rate; zero critical vulnerability scan", "Week 18", "Pending"],
        ["MS-8", "Final System Deployment", "Production deployment on AWS/Docker, User Manual & Final Sign-Off", "Week 20", "Pending"]
    ]
    format_table(doc.add_table(rows=1, cols=5), col_widths_m, headers_m, data_m)

    add_h2("5.3 20-Week Project Implementation Timeline (Gantt Schedule)")
    add_p("The table below details the execution schedule across 10 Sprints (20 Weeks):")

    col_widths_g = [1.8, 0.8, 0.8, 3.1]
    headers_g = ["Phase / Activity Description", "Start Week", "End Week", "Sprint Allocation & Focus"]
    data_g = [
        ["Phase 1: Architecture & SRS", "Week 1", "Week 2", "Sprint 1: Requirements analysis, lit review & system design"],
        ["Phase 2: DB & Auth Backend", "Week 3", "Week 4", "Sprint 2: MySQL schema, MongoDB setup, JWT Authentication"],
        ["Phase 3: Question Bank Engine", "Week 5", "Week 6", "Sprint 3: Subject/Topic management, item creation APIs"],
        ["Phase 4: AI NLP & CAT Engine", "Week 7", "Week 10", "Sprint 4-5: Adaptive logic, GPT/BERT evaluation, fallback"],
        ["Phase 5: Student Testing Interface", "Week 11", "Week 12", "Sprint 6: React test player UI, confidence selector"],
        ["Phase 6: Diagnostic Analytics UI", "Week 13", "Week 15", "Sprint 7-8: 2x2 Matrix computation, faculty analytics dashboard"],
        ["Phase 7: Integration & UAT", "Week 16", "Week 18", "Sprint 9: Security hardening, load testing, UAT execution"],
        ["Phase 8: Deployment & Handover", "Week 19", "Week 20", "Sprint 10: AWS Docker deployment, final documentation"]
    ]
    format_table(doc.add_table(rows=1, cols=4), col_widths_g, headers_g, data_g)

    add_h2("5.4 Risk Management & Mitigation Matrix")

    col_widths_r = [0.8, 1.4, 0.8, 1.8, 1.7]
    headers_r = ["Risk ID", "Risk Description", "Severity", "Mitigation Strategy", "Contingency Plan"]
    data_r = [
        ["RSK-1", "OpenAI API latency (> 3s) or outage impacting subjective evaluation", "HIGH", "Implement 3-second timeout and asynchronous queuing", "Fallback to local SequenceMatcher lexical similarity scoring"],
        ["RSK-2", "Low initial faculty adoption or question bank population friction", "MEDIUM", "Provide CSV bulk-upload tool and pre-built domain templates", "Conduct faculty training workshops and offer initial content support"],
        ["RSK-3", "Student gaming of confidence rating (e.g. always choosing High)", "MEDIUM", "Apply strict -15 penalty score for Overconfident wrong answers", "Incorporate metacognitive calibration warnings in diagnostic report"],
        ["RSK-4", "Database connection bottlenecks under peak exam load", "HIGH", "Implement DB connection pooling (100 max connections) & Redis caching", "Scale database instances vertically and enable read-replicas"],
        ["RSK-5", "Data privacy breach or unauthenticated student record access", "CRITICAL", "Strict JWT role validation, encryption at rest/transit, audit logging", "Immediate session invalidation and automated security alert triggers"]
    ]
    format_table(doc.add_table(rows=1, cols=5), col_widths_r, headers_r, data_r)

    # Conclusion & Sign-Off
    add_h1("6. Conclusion & Document Sign-Off")
    add_p(
        "The proposed AI-Based Real-Time Student Academic Performance Monitoring System represents a paradigm shift from traditional, delayed assessment methods to an intelligent, metacognitive evaluation platform. By bridging Computerized Adaptive Testing, NLP answer scoring, and 2x2 Confidence Matrix analytics, the system empowers students with deep self-awareness and provides faculty with actionable pedagogical insights."
    )
    add_p(
        "All requirements, architecture patterns, and project plans outlined in this document have been validated against technical feasibility constraints and are ready for full execution."
    )

    doc.save("AI_Student_Performance_System_Documentation.docx")
    print("Successfully generated AI_Student_Performance_System_Documentation.docx")

if __name__ == "__main__":
    create_document()
