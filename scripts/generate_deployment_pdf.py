import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#71717a"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "JobTrack — Render.com & Supabase Key Vault Deployment Guide")
            self.setStrokeColor(colors.HexColor("#e4e4e7"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "Strictly Confidential — Production Key Vault & Deployment Reference")
        self.setStrokeColor(colors.HexColor("#e4e4e7"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def build_pdf(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    # Custom palette
    primary_color = colors.HexColor("#0f172a")    # Deep slate
    accent_color = colors.HexColor("#0284c7")     # Sky blue
    success_color = colors.HexColor("#16a34a")    # Emerald
    warning_color = colors.HexColor("#d97706")    # Amber
    border_color = colors.HexColor("#000000")     # Sandal / crisp black
    card_bg = colors.HexColor("#f8fafc")          # Light canvas
    code_bg = colors.HexColor("#1e293b")          # Dark code box

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#000000"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284c7"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#38bdf8"),
        spaceBefore=3,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell_code = ParagraphStyle(
        'TableCellCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0369a1")
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title Banner
    story.append(Paragraph("Render.com & Supabase Key Vault Deployment Guide", title_style))
    story.append(Paragraph("<b>JobTrack Application</b> — Complete step-by-step instructions to extract API keys from Supabase and Redis, configure Render Key Vault, and deploy with strict two-user authentication.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#000000"), spaceBefore=2, spaceAfter=14))

    # Callout: Authorized Users Notice
    user_callout_data = [
        [
            Paragraph("<b>IMPORTANT — STRICT TWO-USER PRODUCTION RESTRICTION:</b><br/>"
                      "The codebase is configured so that <b>only 2 users</b> can access this application:<br/>"
                      "&bull; <b>User 1 (Admin/Superuser):</b> <font color='#0284c7'><b>kanishkan</b></font> &nbsp;|&nbsp; Password: <font color='#b91c1c'><b>Kanishkan@2004</b></font><br/>"
                      "&bull; <b>User 2 (Standard User):</b> <font color='#0284c7'><b>preetha</b></font> &nbsp;|&nbsp; Password: <font color='#b91c1c'><b>Preetha@2005</b></font><br/>"
                      "Both credentials are read directly from Render's Key Vault / Environment Variables during the automated build and migration phase. Any non-authorized demo accounts are automatically purged.", callout_style)
        ]
    ]
    user_callout_table = Table(user_callout_data, colWidths=[504])
    user_callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
        ('BORDER', (0, 0), (-1, -1), 1.5, colors.HexColor("#f59e0b")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(user_callout_table)
    story.append(Spacer(1, 14))

    # Section 1: Overview of Repository Deployment Files
    story.append(Paragraph("1. Prepared Repository Deployment Files", h1_style))
    story.append(Paragraph("The following production files have been created in your project root to ensure a 100% automated Render.com deployment:", body_style))

    repo_files_data = [
        [Paragraph("File Name", table_header_style), Paragraph("Purpose in Render Deployment", table_header_style)],
        [Paragraph("build.sh", table_cell_code), Paragraph("Automated build script. Runs pip install, collectstatic, database migrations, and provisions the 2 Key Vault users.", table_cell_style)],
        [Paragraph("Procfile", table_cell_code), Paragraph("Declares the web process: <code>web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT</code>", table_cell_style)],
        [Paragraph("render.yaml", table_cell_code), Paragraph("Render Blueprint (Infrastructure as Code) that declares the web service, build/start commands, and Key Vault variable mapping.", table_cell_style)],
        [Paragraph(".python-version", table_cell_code), Paragraph("Pins the Python engine version to <code>3.14.0</code> for Render buildpacks.", table_cell_style)],
        [Paragraph("requirements.txt", table_cell_code), Paragraph("Includes Django, whitenoise, dj-database-url, psycopg2-binary (PostgreSQL), redis, and gunicorn.", table_cell_style)],
        [Paragraph("setup_production_users.py", table_cell_code), Paragraph("Django command that strictly verifies, syncs passwords, and provisions <code>kanishkan</code> and <code>preetha</code>.", table_cell_style)],
        [Paragraph("supabase_client.py", table_cell_code), Paragraph("Supabase storage client for persistent resume & document storage without external dependencies.", table_cell_style)],
    ]
    repo_table = Table(repo_files_data, colWidths=[150, 354])
    repo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(repo_table)
    story.append(Spacer(1, 16))

    # Section 2: Complete Key Vault Environment Variables Table
    story.append(Paragraph("2. Complete Render.com Key Vault Variables Table", h1_style))
    story.append(Paragraph("In your Render Dashboard, go to your Web Service &rarr; <b>Environment</b> (or <b>Key Vault</b>) &rarr; <b>Add Environment Variable</b> for each key below:", body_style))

    vault_data = [
        [Paragraph("Key Name", table_header_style), Paragraph("Recommended Value / Format", table_header_style), Paragraph("Source / Instructions", table_header_style)],
        [Paragraph("ALLOWED_HOSTS", table_cell_code), Paragraph("<code>localhost,127.0.0.1,.onrender.com,your-app.onrender.com</code>", table_cell_style), Paragraph("Add your custom domain or Render assigned subdomain.", table_cell_style)],
        [Paragraph("DATABASE_URL", table_cell_code), Paragraph("<code>postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres</code>", table_cell_style), Paragraph("Copied from Supabase Database URI string (see Step 3A).", table_cell_style)],
        [Paragraph("DEBUG", table_cell_code), Paragraph("<code>False</code>", table_cell_style), Paragraph("Strictly False in production for maximum security.", table_cell_style)],
        [Paragraph("SECRET_KEY", table_cell_code), Paragraph("<code>django-insecure-prod-key-xyz... (or 50+ random characters)</code>", table_cell_style), Paragraph("Cryptographic key. Render can also auto-generate.", table_cell_style)],
        [Paragraph("PYTHON_VERSION", table_cell_code), Paragraph("<code>3.14.0</code>", table_cell_style), Paragraph("Instructs Render to run Python 3.14.", table_cell_style)],
        [Paragraph("REDIS_URL", table_cell_code), Paragraph("<code>redis://red-xxxx:6379</code>", table_cell_style), Paragraph("From Render Redis (free tier) or Upstash (see Step 3B).", table_cell_style)],
        [Paragraph("HEALTHCHECK_APPLICATION_URL", table_cell_code), Paragraph("<code>https://your-app.onrender.com</code>", table_cell_style), Paragraph("Your live Render web service URL.", table_cell_style)],
        [Paragraph("HEALTHCHECK_ADMIN_USERNAME", table_cell_code), Paragraph("<code>kanishkan</code>", table_cell_style), Paragraph("Verified by /health/ endpoint as the superuser.", table_cell_style)],
        [Paragraph("HEALTHCHECK_TIME_ZONE", table_cell_code), Paragraph("<code>UTC</code> (or <code>Asia/Kolkata</code>)", table_cell_style), Paragraph("Application operational time zone.", table_cell_style)],
        [Paragraph("SUPABASE_URL", table_cell_code), Paragraph("<code>https://[PROJECT-REF].supabase.co</code>", table_cell_style), Paragraph("Supabase Project Settings &rarr; API &rarr; Project URL.", table_cell_style)],
        [Paragraph("SUPABASE_SERVICE_ROLE_KEY", table_cell_code), Paragraph("<code>eyJhbGciOi... (secret service_role key)</code>", table_cell_style), Paragraph("Supabase Project Settings &rarr; API &rarr; service_role.", table_cell_style)],
        [Paragraph("SUPABASE_STORAGE_BUCKET", table_cell_code), Paragraph("<code>resumes</code>", table_cell_style), Paragraph("Supabase Storage bucket name for file uploads.", table_cell_style)],
        [Paragraph("USER_1_USERNAME", table_cell_code), Paragraph("<code>kanishkan</code>", table_cell_style), Paragraph("Superuser / Admin account username.", table_cell_style)],
        [Paragraph("USER_1_PASSWORD", table_cell_code), Paragraph("<code>Kanishkan@2004</code>", table_cell_style), Paragraph("Admin password configured in Key Vault.", table_cell_style)],
        [Paragraph("USER_2_USERNAME", table_cell_code), Paragraph("<code>preetha</code>", table_cell_style), Paragraph("Second authorized user username.", table_cell_style)],
        [Paragraph("USER_2_PASSWORD", table_cell_code), Paragraph("<code>Preetha@2005</code>", table_cell_style), Paragraph("Password for user preetha.", table_cell_style)],
    ]
    vault_table = Table(vault_data, colWidths=[140, 204, 160])
    vault_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(vault_table)

    story.append(PageBreak())

    # Section 3: How to Extract Keys from External Providers
    story.append(Paragraph("3. How to Extract Every API Key & Value", h1_style))
    story.append(Paragraph("Follow these visual step-by-step instructions to get your credentials from Supabase, Redis, and Render:", body_style))

    # Step 3A: Supabase Database URL
    story.append(Paragraph("Step 3A: How to Get DATABASE_URL from Supabase", h2_style))
    story.append(Paragraph("&bull; Log in to your <a href='https://supabase.com/dashboard'>Supabase Dashboard</a> and open your project.", bullet_style))
    story.append(Paragraph("&bull; In the left sidebar, click <b>Project Settings</b> (gear icon at the bottom).", bullet_style))
    story.append(Paragraph("&bull; Click <b>Database</b> under Configuration.", bullet_style))
    story.append(Paragraph("&bull; Scroll down to the <b>Connection string</b> section and click the <b>URI</b> tab.", bullet_style))
    story.append(Paragraph("&bull; Select <b>Node.js / Python / URI</b>. You will see a string like:<br/>"
                           "&nbsp;&nbsp;<code>postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres</code><br/>"
                           "&nbsp;&nbsp;<i>(Or if using the Transaction Pooler for IPv4: port 6543)</i>", bullet_style))
    story.append(Paragraph("&bull; Replace <code>[YOUR-PASSWORD]</code> with your actual Supabase database password.", bullet_style))
    story.append(Paragraph("&bull; Copy this full string into Render's <b>DATABASE_URL</b> key.", bullet_style))

    # Step 3B: Supabase Storage & API Keys
    story.append(Paragraph("Step 3B: How to Get SUPABASE_URL, SERVICE_ROLE_KEY & STORAGE_BUCKET", h2_style))
    story.append(Paragraph("&bull; In Supabase Project Settings, click <b>API</b> in the sidebar.", bullet_style))
    story.append(Paragraph("&bull; <b>SUPABASE_URL:</b> Look at <b>Project URL</b>. Copy the URL (e.g. <code>https://abcdefghijklm.supabase.co</code>).", bullet_style))
    story.append(Paragraph("&bull; <b>SUPABASE_SERVICE_ROLE_KEY:</b> In the <b>Project API keys</b> section, find <code>service_role</code> (secret). Click <b>Reveal secret key</b> and copy it. <i>(Do not use the public anon key for server-side operations)</i>.", bullet_style))
    story.append(Paragraph("&bull; <b>SUPABASE_STORAGE_BUCKET:</b> In the left navigation, click <b>Storage</b> &rarr; <b>New Bucket</b> &rarr; enter <code>resumes</code> &rarr; click <b>Create bucket</b>. Set this as <code>resumes</code> in Render.", bullet_style))

    # Step 3C: Redis URL
    story.append(Paragraph("Step 3C: How to Get REDIS_URL from Render or Upstash", h2_style))
    story.append(Paragraph("&bull; <b>Option 1 (Render Redis - Recommended):</b> On Render dashboard, click <b>New +</b> &rarr; <b>Redis</b> &rarr; Name it <code>jobtrack-redis</code> &rarr; Select Free plan &rarr; Click <b>Create Redis</b>. Copy the <b>Internal Redis URL</b> (e.g. <code>redis://red-xxxx:6379</code>).", bullet_style))
    story.append(Paragraph("&bull; <b>Option 2 (Upstash Redis):</b> Log into <a href='https://upstash.com'>Upstash</a>, create a free Redis database, and copy the standard Redis connection string (<code>rediss://default:xxxx@host:port</code>).", bullet_style))
    story.append(Paragraph("&bull; <i>Note:</i> If you do not have Redis yet, leave <code>REDIS_URL</code> blank or commented out. Django will automatically fall back to its high-speed in-memory cache without any errors.", bullet_style))

    # Step 3D: Healthcheck & Application URL
    story.append(Paragraph("Step 3D: Setting HEALTHCHECK_APPLICATION_URL & ADMIN_USERNAME", h2_style))
    story.append(Paragraph("&bull; Once your Render web service is created, Render will give you a domain: <code>https://ai-learning-tracker.onrender.com</code> (or custom domain).", bullet_style))
    story.append(Paragraph("&bull; Set <b>HEALTHCHECK_APPLICATION_URL</b> to that exact URL.", bullet_style))
    story.append(Paragraph("&bull; Set <b>HEALTHCHECK_ADMIN_USERNAME</b> to <code>kanishkan</code>.", bullet_style))
    story.append(Paragraph("&bull; Render will ping <code>/health/</code> automatically every few seconds to monitor your deployment.", bullet_style))

    story.append(Spacer(1, 10))

    # Section 4: Render Deployment Walkthrough
    story.append(Paragraph("4. Step-by-Step Render.com Deployment Walkthrough", h1_style))

    story.append(Paragraph("Follow these 6 steps to deploy your repository to Render.com:", body_style))

    deploy_steps = [
        ("Step 1: Push Code to GitHub",
         "Commit and push all modified files to your GitHub repository:<br/>"
         "<code>git add . && git commit -m 'Configure Render deployment and Key Vault' && git push origin main</code>"),
        ("Step 2: Create Web Service on Render",
         "Go to <b>https://dashboard.render.com</b> &rarr; Click <b>New +</b> &rarr; Select <b>Web Service</b> &rarr; Choose <b>Build and deploy from a Git repository</b> &rarr; Connect your GitHub repository."),
        ("Step 3: Configure Basic Settings",
         "&bull; <b>Name:</b> <code>ai-learning-tracker</code> (or your chosen name)<br/>"
         "&bull; <b>Region:</b> Select nearest region (e.g., Oregon or Frankfurt)<br/>"
         "&bull; <b>Branch:</b> <code>main</code><br/>"
         "&bull; <b>Runtime:</b> <code>Python 3</code><br/>"
         "&bull; <b>Build Command:</b> <code>chmod +x build.sh && ./build.sh</code><br/>"
         "&bull; <b>Start Command:</b> <code>gunicorn config.wsgi:application --bind 0.0.0.0:$PORT</code>"),
        ("Step 4: Enter Key Vault / Environment Variables",
         "Scroll down to <b>Environment Variables</b> (or click the <b>Environment</b> tab) &rarr; Click <b>Add Environment Variable</b> &rarr; Paste all 17 keys from Section 2."),
        ("Step 5: Set Health Check Path",
         "Click <b>Advanced</b> &rarr; Look for <b>Health Check Path</b> &rarr; Enter <code>/health/</code> &rarr; Click <b>Create Web Service</b>."),
        ("Step 6: Confirm Deployment & Log In",
         "Render will run <code>build.sh</code>, run migrations, and execute <code>setup_production_users</code>.<br/>"
         "Check the deploy logs. You should see:<br/>"
         "<code>[OK] Created user 'kanishkan' (Superuser/Admin) with Key Vault credentials.</code><br/>"
         "<code>[OK] Created user 'preetha' (Standard User) with Key Vault credentials.</code><br/>"
         "Now navigate to your live URL and log in!")
    ]

    for title, desc in deploy_steps:
        box_data = [
            [Paragraph(f"<b>{title}</b>", table_header_style)],
            [Paragraph(desc, body_style)]
        ]
        box_table = Table(box_data, colWidths=[504])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(box_table)
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Section 5: User Credentials & Post-Deploy Verification
    story.append(Paragraph("5. User Accounts & Verification Checklist", h1_style))

    creds_table_data = [
        [Paragraph("Username", table_header_style), Paragraph("Password", table_header_style), Paragraph("Role", table_header_style), Paragraph("Access Scope", table_header_style)],
        [Paragraph("kanishkan", table_cell_code), Paragraph("Kanishkan@2004", table_cell_bold), Paragraph("Superuser / Admin", table_cell_style), Paragraph("Full access to Django Admin (/admin/), job folders, stats, and settings.", table_cell_style)],
        [Paragraph("preetha", table_cell_code), Paragraph("Preetha@2005", table_cell_bold), Paragraph("Standard User", table_cell_style), Paragraph("Isolated personal job application tracker, entries, folders, and metrics.", table_cell_style)],
    ]
    creds_table = Table(creds_table_data, colWidths=[100, 120, 110, 174])
    creds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(creds_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Post-Deployment Verification Checklist", h2_style))
    checklist_items = [
        "<b>Check Health Endpoint:</b> Visit <code>https://your-app.onrender.com/health/</code> &rarr; Should return HTTP 200 with <code>{\"status\": \"healthy\", \"database\": \"connected\", \"admin_verified\": true}</code>.",
        "<b>Admin Login:</b> Log into <code>https://your-app.onrender.com/login/</code> with username <code>kanishkan</code> and password <code>Kanishkan@2004</code>. Confirm dashboard opens with 5 default folders.",
        "<b>Second User Login:</b> Open an incognito tab and log in with username <code>preetha</code> and password <code>Preetha@2005</code>. Confirm complete data isolation (Preetha cannot see Kanishkan's applications).",
        "<b>Job Application Creation:</b> Create a job under the <code>LinkedIn</code> folder &rarr; Confirm it saves and persists to Supabase PostgreSQL.",
        "<b>CSRF Protection:</b> Ensure <code>HEALTHCHECK_APPLICATION_URL</code> is set so forms submit without CSRF 403 Forbidden errors.",
        "<b>Free-Tier Keep-Alive:</b> If using Render's free tier (spins down after 15m), set up a free monitor (e.g. UptimeRobot or Cron-job.org) to ping <code>https://your-app.onrender.com/health/</code> every 10 minutes."
    ]
    for item in checklist_items:
        story.append(Paragraph(f"&bull; {item}", bullet_style))

    story.append(Spacer(1, 14))

    # Section 6: Quick Troubleshooting
    story.append(Paragraph("6. Common Errors & Quick Solutions", h1_style))
    troubleshoot_data = [
        [Paragraph("Issue / Symptom", table_header_style), Paragraph("Root Cause & Quick Resolution", table_header_style)],
        [
            Paragraph("<b>CSRF verification failed (403)</b>", table_cell_style),
            Paragraph("Render uses HTTPS. Ensure <code>HEALTHCHECK_APPLICATION_URL</code> is set to <code>https://your-app.onrender.com</code>. The settings will automatically authorize your domain.", table_cell_style)
        ],
        [
            Paragraph("<b>Database connection refused</b>", table_cell_style),
            Paragraph("Check your <code>DATABASE_URL</code>. In Supabase, if using IPv4 connections on Render, use port <code>6543</code> (Transaction Pooler) or verify your database password.", table_cell_style)
        ],
        [
            Paragraph("<b>Permission denied: ./build.sh</b>", table_cell_style),
            Paragraph("Make build.sh executable before committing: <code>git update-index --chmod=+x build.sh</code> or set Build Command on Render to <code>bash build.sh</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>Static files missing (CSS unstyled)</b>", table_cell_style),
            Paragraph("WhiteNoise is pre-configured in <code>settings.py</code> and <code>build.sh</code> runs <code>collectstatic</code> automatically. Ensure <code>DEBUG=False</code> so WhiteNoise serves static files.", table_cell_style)
        ],
    ]
    troubleshoot_table = Table(troubleshoot_data, colWidths=[160, 344])
    troubleshoot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(troubleshoot_table)

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_filename}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RENDER_DEPLOYMENT_GUIDE.pdf")
    build_pdf(out_path)
