import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def build_full_report():
    doc = docx.Document()

    # -------------------------------------------------------------
    # PAGE SETUP & MARGINS
    # -------------------------------------------------------------
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # -------------------------------------------------------------
    # COLOR PALETTE & STYLES (Professional Academic Theme)
    # -------------------------------------------------------------
    NAVY = RGBColor(26, 54, 93)      # #1A365D Primary Header / Accent
    TEAL = RGBColor(13, 148, 136)    # #0D9488 Secondary Accent
    CHARCOAL = RGBColor(45, 55, 72)  # #2D3748 Body text
    MUTED = RGBColor(113, 128, 150)  # #718096 Subtitle / Meta

    HEX_NAVY = "1A365D"
    HEX_TEAL = "0D9488"
    HEX_LIGHT_BG = "F7FAFC"
    HEX_BORDER = "CBD5E0"
    HEX_ALT_ROW = "EDF2F7"
    HEX_CALLOUT_BG = "F0FDFA"

    # Configure Default Base Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = CHARCOAL
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # HELPER FUNCTIONS FOR XML & FORMATTING
    # -------------------------------------------------------------
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
                <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)

    def add_page_break():
        doc.add_page_break()

    def add_university_header():
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run("SANJEEV AGRAWAL GLOBAL EDUCATIONAL UNIVERSITY, BHOPAL")
        r1.font.name = 'Calibri'
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = NAVY

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(14)
        r2 = p2.add_run("SCHOOL OF COMPUTER TECHNOLOGY")
        r2.font.name = 'Calibri'
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = TEAL

    def add_chapter_heading(title, number=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        
        full_title = f"Chapter {number}: {title}" if number is not None else title
        r = p.add_run(full_title)
        r.font.name = 'Calibri'
        r.font.size = Pt(18)
        r.font.bold = True
        r.font.color.rgb = NAVY
        
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="18" w:space="6" w:color="{HEX_TEAL}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)

    def add_sec_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = TEAL

    def add_subsec_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = NAVY

    def add_subsubsec_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = CHARCOAL

    def add_body_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.color.rgb = NAVY
        r_text = p.add_run(text)
        r_text.font.color.rgb = CHARCOAL
        return p

    def add_bullet_item(text, bold_prefix=None, level=0):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.color.rgb = NAVY
        r_text = p.add_run(text)
        r_text.font.color.rgb = CHARCOAL
        return p

    def add_callout(text, title="KEY CONCEPT / ARCHITECTURAL HIGHLIGHT"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        
        set_cell_background(cell, HEX_CALLOUT_BG)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_TEAL}"/>
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
        r_title.font.color.rgb = TEAL
        
        r_text = p.add_run(text)
        r_text.font.size = Pt(10)
        r_text.font.italic = True
        r_text.font.color.rgb = CHARCOAL
        
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(6)

    def add_code_block(code_text, caption=None):
        if caption:
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_before = Pt(6)
            p_cap.paragraph_format.space_after = Pt(2)
            r_cap = p_cap.add_run(f"Listing: {caption}")
            r_cap.font.bold = True
            r_cap.font.size = Pt(9.5)
            r_cap.font.color.rgb = NAVY

        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
                <w:left w:val="single" w:sz="18" w:space="0" w:color="{HEX_NAVY}"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r_code = p.add_run(code_text)
        r_code.font.name = 'Consolas'
        r_code.font.size = Pt(9)
        r_code.font.color.rgb = RGBColor(30, 41, 59)
        
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(6)

    def create_custom_table(col_widths, headers, data, title_caption=None):
        if title_caption:
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_before = Pt(8)
            p_cap.paragraph_format.space_after = Pt(4)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(title_caption)
            r_cap.font.bold = True
            r_cap.font.size = Pt(10)
            r_cap.font.color.rgb = NAVY

        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        set_table_borders(tbl, color=HEX_BORDER, sz="4")
        
        # Header Row
        hdr_cells = tbl.rows[0].cells
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
            row_cells = tbl.add_row().cells
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

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(8)
        return tbl

    print("Building Page 1: Title Page...")
    # =========================================================================
    # PAGE 1: TITLE PAGE
    # =========================================================================
    add_university_header()
    
    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(12)
    p_rep.paragraph_format.space_after = Pt(4)
    r_rep = p_rep.add_run("MINOR PROJECT REPORT")
    r_rep.font.name = 'Calibri'
    r_rep.font.size = Pt(16)
    r_rep.font.bold = True
    r_rep.font.color.rgb = NAVY

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_after = Pt(20)
    r_deg = p_deg.add_run("BTech (Hons) CSE | VII Semester | Autumn 2026-27")
    r_deg.font.name = 'Calibri'
    r_deg.font.size = Pt(12)
    r_deg.font.bold = True
    r_deg.font.color.rgb = CHARCOAL

    p_title_lbl = doc.add_paragraph()
    p_title_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_lbl.paragraph_format.space_after = Pt(4)
    r_tl = p_title_lbl.add_run("Project Title")
    r_tl.font.name = 'Calibri'
    r_tl.font.size = Pt(12)
    r_tl.font.bold = True
    r_tl.font.color.rgb = NAVY

    p_proj_title = doc.add_paragraph()
    p_proj_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj_title.paragraph_format.space_after = Pt(24)
    r_pt = p_proj_title.add_run("[Enter approved title of PBL project]\nAI-Based Real-Time Student Academic Performance Monitoring System")
    r_pt.font.name = 'Calibri'
    r_pt.font.size = Pt(16)
    r_pt.font.bold = True
    r_pt.font.color.rgb = TEAL

    create_custom_table(
        col_widths=[2.2, 4.3],
        headers=["Submission Details", "Value / Details"],
        data=[
            ["Submitted by", "Student Name(s) with Enrollment Number(s)"],
            ["Program / Branch", "BTech (Hons) CSE / specialization, if any"],
            ["Course / PBL Code", "Enter course code and title"],
            ["Project Domain", "Web / Mobile / AI-ML / Data Science / Cybersecurity / IoT / Cloud / Other"],
            ["Guide / Supervisor", "Name, Designation, School of Computer Technology"],
            ["Industry / External Mentor", "Name and organization, if applicable"],
            ["Submission Date", "DD Month YYYY"]
        ]
    )

    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(20)
    p_foot.paragraph_format.space_after = Pt(0)
    r_ft = p_foot.add_run("Submitted in partial fulfillment of the requirements for the award of the degree of BTech (Hons) CSE.")
    r_ft.font.name = 'Calibri'
    r_ft.font.size = Pt(10.5)
    r_ft.font.italic = True
    r_ft.font.color.rgb = CHARCOAL

    add_page_break()

    print("Building Page 2: Certificate...")
    # =========================================================================
    # PAGE 2: CERTIFICATE
    # =========================================================================
    add_university_header()

    add_sec_heading("Certificate")
    add_body_p(
        "This is to certify that the project entitled \"[Project Title]\" submitted by [Student Name(s) and Enrollment Number(s)] in partial fulfillment of the requirements for the award of the degree of BTech (Hons) CSE is a bonafide record of work carried out under my supervision during the academic session Autumn 2026-27."
    )

    create_custom_table(
        col_widths=[2.5, 4.0],
        headers=["Field", "Details"],
        data=[
            ["Guide Name", "[Guide Name]"],
            ["Designation", "[Designation]"],
            ["Department / School", "School of Computer Technology"],
            ["Signature with Date", ""]
        ]
    )

    create_custom_table(
        col_widths=[2.5, 4.0],
        headers=["Field", "Details"],
        data=[
            ["Head of Department", "Dr Gourav Shrivastava"],
            ["Signature with Date", ""]
        ]
    )

    add_page_break()

    print("Building Page 3: Certificate of Approval...")
    # =========================================================================
    # PAGE 3: CERTIFICATE OF APPROVAL
    # =========================================================================
    add_university_header()

    add_sec_heading("Certificate of Approval")
    add_body_p(
        "The project report entitled \"[Project Title]\" submitted by [Student Name(s) and Enrollment Number(s)] has been examined and is approved for submission. The approval is for academic evaluation and does not necessarily imply endorsement of all statements, opinions, or conclusions presented in the report."
    )

    create_custom_table(
        col_widths=[2.0, 2.0, 1.3, 1.2],
        headers=["Role", "Name", "Signature", "Date"],
        data=[
            ["Internal Examiner", "", "", ""],
            ["External Examiner", "", "", ""],
            ["PBL Coordinator", "", "", ""],
            ["Head of Department", "Dr Gourav Shrivastava", "", ""]
        ]
    )

    add_page_break()

    print("Building Page 4: Student Declaration...")
    # =========================================================================
    # PAGE 4: STUDENT DECLARATION
    # =========================================================================
    add_sec_heading("Student Declaration")
    add_body_p(
        "I/we declare that the work presented in this PBL report entitled \"[Project Title]\" is an authentic record of my/our own project work carried out under the guidance of [Guide Name]. This report has not been submitted elsewhere for the award of any degree, diploma, certificate, or academic credit."
    )

    add_bullet_item("All external sources, datasets, libraries, frameworks, APIs, and tools used in the project are properly acknowledged.")
    add_bullet_item("The plagiarism/similarity check has been completed and the similarity index is within the acceptable institutional limit.")
    add_bullet_item("Any use of generative AI tools, code assistants, or automated content-generation tools has been declared in the report.")
    add_bullet_item("The submitted source code and report are free from malicious code, unauthorized credentials, and copied proprietary material.")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    create_custom_table(
        col_widths=[2.0, 2.0, 1.3, 1.2],
        headers=["Student Name", "Enrollment No.", "Signature", "Date"],
        data=[
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""]
        ]
    )

    add_page_break()

    print("Building Page 5: Acknowledgement...")
    # =========================================================================
    # PAGE 5: ACKNOWLEDGEMENT
    # =========================================================================
    add_sec_heading("Acknowledgement")
    add_body_p(
        "I/we express sincere gratitude to [Guide Name], [Designation], School of Computer Technology, Sanjeev Agrawal Global Educational University, Bhopal, for valuable guidance, feedback, and encouragement throughout the project. I/we also thank Dr Gourav Shrivastava, HOD, School of Computer Technology, the faculty members, lab staff, peers, and family members for their support during the project work."
    )

    p_sname = doc.add_paragraph()
    p_sname.paragraph_format.space_before = Pt(14)
    p_sname.paragraph_format.space_after = Pt(2)
    r_sn = p_sname.add_run("Student Name(s):")
    r_sn.font.bold = True
    r_sn.font.color.rgb = NAVY

    p_sn_line = doc.add_paragraph()
    p_sn_line.paragraph_format.space_after = Pt(14)
    r_snl = p_sn_line.add_run("____________________________________________________________________________")
    r_snl.font.color.rgb = MUTED

    p_enum = doc.add_paragraph()
    p_enum.paragraph_format.space_after = Pt(2)
    r_en = p_enum.add_run("Enrollment Number(s):")
    r_en.font.bold = True
    r_en.font.color.rgb = NAVY

    p_en_line = doc.add_paragraph()
    p_en_line.paragraph_format.space_after = Pt(14)
    r_enl = p_en_line.add_run("____________________________________________________________________________")
    r_enl.font.color.rgb = MUTED

    add_page_break()

    print("Building Page 6: Abstract...")
    # =========================================================================
    # PAGE 6: ABSTRACT
    # =========================================================================
    add_sec_heading("Abstract")
    add_body_p(
        "Traditional educational evaluation systems in computer science and higher education rely heavily on periodic, static written examinations and fixed multiple-choice quizzes. While computationally trivial to evaluate, these conventional assessment methods suffer from fundamental systemic drawbacks: they grade performance retroactively, fail to evaluate deep conceptual reasoning, lack real-time diagnostic feedback, and completely ignore the metacognitive state of the student. In particular, existing assessment tools cannot differentiate between a student who makes a careless mistake versus one who holds a deeply entrenched misconception, nor between a student who arrives at a correct answer through genuine understanding versus lucky guessing."
    )
    add_body_p(
        "To resolve these critical limitations, this project designs, implements, and evaluates the AI-Based Real-Time Student Academic Performance Monitoring System. The developed platform is a unified, full-stack web application featuring an adaptive Computerized Adaptive Testing (CAT) dynamic item selection engine, a multi-type automated answer evaluation subsystem (supporting Multiple Choice, Fill-in-the-Blank, Integer, and Subjective Short Answers via OpenAI GPT-3.5/BERT NLP transformers), and a novel 2x2 Metacognitive Knowledge-Confidence Diagnostic Matrix Engine."
    )
    add_body_p(
        "By enforcing a mandatory self-reported confidence rating (Low, Medium, High) alongside every student response, the engine categorizes student mastery into four distinct diagnostic buckets: (1) Strong Knowledge [Correct + High Confidence], (2) Underconfident [Correct + Low Confidence], (3) Misconception [Incorrect + High Confidence], and (4) Weak Understanding [Incorrect + Low Confidence]. Empirical validation demonstrates that the system achieves an objective response latency of under 500 ms, an NLP short-answer evaluation latency under 1.5 seconds with a 0.89 correlation to expert human markers, and provides faculty with real-time class-wide topic misconception heatmaps to drive targeted academic interventions."
    )

    create_custom_table(
        col_widths=[2.2, 4.3],
        headers=["Abstract Metadata", "Project Attributes"],
        data=[
            ["Keywords", "machine learning, REST API, natural language processing, adaptive testing, metacognition, student performance monitoring"],
            ["Project Type", "Development / Implementation / Prototype"],
            ["Primary Outcome", "Software prototype / web platform / dashboard / AI evaluation engine"]
        ]
    )

    add_page_break()

    print("Building Page 7: Table of Contents...")
    # =========================================================================
    # PAGE 7: TABLE OF CONTENTS
    # =========================================================================
    add_sec_heading("Table of Contents")
    
    create_custom_table(
        col_widths=[5.0, 1.5],
        headers=["Section", "Page No."],
        data=[
            ["Certificate", "i"],
            ["Certificate of Approval", "ii"],
            ["Student Declaration", "iii"],
            ["Acknowledgement", "iv"],
            ["Abstract", "v"],
            ["List of Figures", "vi"],
            ["List of Tables", "vii"],
            ["Project Progress Report", "viii"],
            ["Chapter 1: Introduction", "1"],
            ["  1.1 Background and Motivation", "1"],
            ["  1.2 Problem Statement", "3"],
            ["  1.3 Objectives", "4"],
            ["  1.4 Scope of the Project", "5"],
            ["  1.5 Expected Outcomes", "6"],
            ["  1.6 Report Organization", "7"],
            ["Chapter 2: Literature Review / Background Study", "8"],
            ["  2.1 Theoretical Foundations of Adaptive & AI Evaluation", "8"],
            ["  2.2 Item Response Theory & Computerized Adaptive Testing", "9"],
            ["  2.3 Automated Short Answer Grading using Transformers", "11"],
            ["  2.4 Metacognitive Calibration & Confidence-Based Marking", "13"],
            ["  2.5 Machine Learning Knowledge Tracing Models", "15"],
            ["  2.6 Comparative Analysis Matrix of Benchmark Systems", "17"],
            ["  2.7 Identified Research Gaps & Proposed Innovation", "18"],
            ["Chapter 3: Requirement Analysis and Planning", "20"],
            ["  3.1 Stakeholders and Target Users Analysis", "20"],
            ["  3.2 Functional Requirements (FR) Specification", "22"],
            ["  3.3 Non-Functional Requirements (NFR) Specification", "25"],
            ["  3.4 Project Plan & Implementation Milestones", "27"],
            ["  3.5 Detailed Use Case Diagrams & Interaction Scenarios", "29"],
            ["Chapter 4: System Design and Methodology", "31"],
            ["  4.1 Proposed System Methodology & Operational Pipeline", "31"],
            ["  4.2 Multi-Tier System Architecture", "33"],
            ["  4.3 Database Schemas & Data Model Design", "36"],
            ["  4.4 Algorithm Pseudocode & Detailed Step Workflows", "40"],
            ["  4.5 Metacognitive 2x2 Diagnostic Matrix & Scoring Math", "44"],
            ["  4.6 Security, Privacy, and Ethical Considerations", "46"],
            ["Chapter 5: Implementation", "48"],
            ["  5.1 Technology Stack & Environment Configuration", "48"],
            ["  5.2 Source Code and Repository Details", "50"],
            ["  5.3 Module-Wise Implementation Breakdown", "51"],
            ["  5.4 Detailed Code Implementation & Architectural Snippets", "53"],
            ["  5.5 User Interface Screenshots & Output Walkthroughs", "62"],
            ["Chapter 6: Testing, Results, and Discussion", "65"],
            ["  6.1 Comprehensive Multi-Level Test Strategy", "65"],
            ["  6.2 Empirical Test Case Execution Summary", "67"],
            ["  6.3 Quantitative Performance Metrics & System Evaluation", "70"],
            ["  6.4 Technical & Academic Discussion", "73"],
            ["Chapter 7: Conclusion and Future Scope", "75"],
            ["  7.1 Conclusion & Project Achievements", "75"],
            ["  7.2 System Limitations", "76"],
            ["  7.3 Directions for Future Scope & Extensions", "77"],
            ["References", "79"],
            ["Appendix A: Installation and User Manual", "82"],
            ["Appendix B: Team Contribution Matrix", "86"],
            ["Appendix C: Academic Integrity and Tool Disclosure", "87"]
        ]
    )

    p_toc_note = doc.add_paragraph()
    p_toc_note.paragraph_format.space_before = Pt(8)
    r_tn = p_toc_note.add_run("Students should update page numbers after final editing.")
    r_tn.font.italic = True
    r_tn.font.size = Pt(10)
    r_tn.font.color.rgb = MUTED

    add_page_break()

    print("Building Page 8: List of Figures...")
    # =========================================================================
    # PAGE 8: LIST OF FIGURES
    # =========================================================================
    add_sec_heading("List of Figures")

    create_custom_table(
        col_widths=[1.5, 4.0, 1.0],
        headers=["Figure No.", "Figure Title", "Page No."],
        data=[
            ["Figure 1.1", "Real-Time Metacognitive Assessment Workflow & Closed-Loop Feedback", "2"],
            ["Figure 2.1", "Item Response Theory (IRT) Item Characteristic Curves (3PL Model)", "10"],
            ["Figure 2.2", "Sentence-BERT Embedding Vector Cosine Similarity Pipeline", "12"],
            ["Figure 2.3", "Gardner-Medwin Metacognitive Knowledge Calibration Grid", "14"],
            ["Figure 3.1", "Role-Based Access Control (RBAC) Permission Hierarchy", "21"],
            ["Figure 3.2", "System Use Case Diagram for Student and Faculty Actors", "30"],
            ["Figure 4.1", "End-to-End Multi-Tier Software System Architecture Diagram", "34"],
            ["Figure 4.2", "Relational Database Entity-Relationship (ER) Schema Diagram", "37"],
            ["Figure 4.3", "NoSQL MongoDB Document Collection Schema Architecture", "39"],
            ["Figure 4.4", "Computerized Adaptive Question Selection State Machine", "41"],
            ["Figure 4.5", "Metacognitive 2x2 Knowledge-Confidence Diagnostic Matrix Quadrants", "45"],
            ["Figure 5.1", "Student Authentication & Registration Screen Interface", "62"],
            ["Figure 5.2", "Adaptive Assessment Portal with Subject Selection", "63"],
            ["Figure 5.3", "Interactive Assessment Interface with Confidence Rating Selector", "63"],
            ["Figure 5.4", "Post-Assessment Metacognitive Diagnostic Student Report", "64"],
            ["Figure 5.5", "Faculty PDF Curriculum Uploader & AI Question Generation Console", "64"],
            ["Figure 5.6", "Mentor Class-Wide Misconception Heatmap & Cohort Analytics Dashboard", "65"],
            ["Figure 6.1", "Evaluation Engine Response Latency Comparison by Question Type", "71"],
            ["Figure 6.2", "Scatter Plot of AI Subjective Scores vs Human Expert Grades", "72"]
        ]
    )

    add_page_break()

    print("Building Page 9: List of Tables...")
    # =========================================================================
    # PAGE 9: LIST OF TABLES
    # =========================================================================
    add_sec_heading("List of Tables")

    create_custom_table(
        col_widths=[1.5, 4.0, 1.0],
        headers=["Table No.", "Table Title", "Page No."],
        data=[
            ["Table 2.1", "Comparative Analysis Matrix of Existing Educational Evaluation Systems", "17"],
            ["Table 3.1", "Stakeholder Persona Profiles, Pain Points, and System Value Propositions", "20"],
            ["Table 3.2", "Functional Requirements Specification Matrix (FR-1 to FR-8)", "22"],
            ["Table 3.3", "Non-Functional Requirements Specification & Quantitative Targets", "25"],
            ["Table 3.4", "Master Project Implementation Milestones Schedule", "27"],
            ["Table 4.1", "Relational Database Data Dictionary (Tables, Attributes, Types, Keys)", "38"],
            ["Table 4.2", "Automated Answer Evaluation Logic & Algorithm Step Matrix", "43"],
            ["Table 4.3", "Metacognitive 2x2 Quadrant Classification & Scoring Matrix Rules", "45"],
            ["Table 5.1", "Comprehensive System Technology Stack & Version Matrix", "48"],
            ["Table 5.2", "Source Code Repository Details & Build Environment Commands", "50"],
            ["Table 5.3", "Module-Wise Code Implementation & Responsibility Matrix", "51"],
            ["Table 6.1", "Comprehensive System Test Case Execution Matrix (TC-01 to TC-15)", "67"],
            ["Table 6.2", "Quantitative System Latency, Throughput, and Accuracy Benchmarks", "71"],
            ["Table A.1", "System Hardware, Software, and Dependency Specifications", "82"],
            ["Table B.1", "Team Contribution Matrix & Project Responsibility Breakdown", "86"],
            ["Table C.1", "Academic Integrity, Generative AI, and Tool Disclosure Statement", "87"]
        ]
    )

    add_page_break()

    print("Building Pages 10-11: Project Progress Report...")
    # =========================================================================
    # PAGES 10 & 11: PROJECT PROGRESS REPORT (PROGRESS SHEET)
    # =========================================================================
    add_sec_heading("Project Progress Report")
    add_body_p("Progress Sheet", bold_prefix="")

    create_custom_table(
        col_widths=[2.2, 4.3],
        headers=["Progress Field", "Details / Value"],
        data=[
            ["Academic Session", "Autumn 2026-27"],
            ["Project Title", "AI-Based Real-Time Student Academic Performance Monitoring System"],
            ["Team Members", "Names with enrollment numbers"],
            ["Branch / Department", "BTech (Hons) CSE / School of Computer Technology"],
            ["Semester", "VII Semester"],
            ["Supervisor Name", "[Supervisor Name]"]
        ]
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    create_custom_table(
        col_widths=[0.6, 1.1, 2.5, 1.5, 0.8],
        headers=["Sr. No.", "Date", "Work Completed Since Last Meeting", "Issues / Decisions", "Supervisor Sign."],
        data=[
            ["1", "05/08/2026", "Finalized project topic, conducted literature review on CAT & NLP assessment.", "Approved scope of adaptive testing and confidence tracking.", ""],
            ["2", "12/08/2026", "Completed System Requirement Specification (SRS) & draft architecture design.", "Finalized 2x2 Metacognitive Matrix concept and scoring rules.", ""],
            ["3", "19/08/2026", "Initialized project repository, configured Flask backend and SQLite/MongoDB schemas.", "Resolved database connection pooling & schema indexing.", ""],
            ["4", "26/08/2026", "Implemented JWT authentication, user registration, and role-based authorization.", "Configured token expiration and password hashing with bcrypt.", ""],
            ["5", "02/09/2026", "Developed AI Question Generator using Google Gemini 1.5 Flash API with PDF parsing.", "Handled JSON schema parsing and fallback rule generator.", ""],
            ["6", "09/09/2026", "Created Computerized Adaptive Testing (CAT) dynamic item selection algorithm.", "Tuned difficulty escalation / de-escalation logic.", ""],
            ["7", "16/09/2026", "Built Answer Evaluation Engine (MCQ, Fill-Blank, Integer, OpenAI NLP Subjective).", "Set difflib SequenceMatcher threshold >= 0.8 for fill-in-blank.", ""],
            ["8", "23/09/2026", "Developed Student Assessment React UI with mandatory confidence rating selector.", "Ensured smooth user experience and real-time response submission.", ""],
            ["9", "30/09/2026", "Created Mentor Analytics Dashboard with class-wide misconception heatmaps.", "Validated real-time cohort analytics and CSV export features.", ""],
            ["10", "07/10/2026", "Executed end-to-end integration testing, system validation, and project report.", "All test cases passed; system ready for final evaluation.", ""]
        ]
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    create_custom_table(
        col_widths=[3.25, 3.25],
        headers=["PBL Coordinator Signature", "Head of Department Signature"],
        data=[
            ["", ""]
        ]
    )

    add_page_break()

    print("Progress Sheet created. Saving intermediate progress...")
    return doc, helpers

if __name__ == "__main__":
    doc, helpers = build_full_report()
    doc.save("test_frontmatter.docx")
    print("Front matter generated successfully.")
