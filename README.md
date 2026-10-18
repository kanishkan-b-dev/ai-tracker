# JobTrack — Sanity-Inspired Job Search Operations Platform

JobTrack is a full-featured, developer-first job application tracking workspace built with **Django** and a dark-mode visual design adapted from **[Sanity.io](https://www.sanity.io)**.

---

## 🚀 Key Features

1. **Authentication & User Data Isolation**
   - Secure Django registration, authentication, login/logout, and password update.
   - Sessions expire 15 minutes after login, even while active, with a visible countdown and a 30-second warning.
   - Strict database-level isolation: Each user only accesses their own applications, interviews, notes, contacts, and telemetry.

2. **Operations Dashboard**
   - Live database metrics: Total Applications, Applied, Interviews in Progress, Offers Received, Follow-ups Due.
   - Upcoming interview timeline and overdue follow-up alerts.
   - Audit activity stream tracking application creation, status transitions, and note updates.

3. **Job Application Management (CRUD)**
   - Complete workflow: `Interested` &rarr; `Applied` &rarr; `Assessment` &rarr; `Interview` &rarr; `Offer` &rarr; `Rejected` &rarr; `Withdrawn`.
   - Real-time search by company, job title, and skills.
   - Multi-parameter filtering by status, work arrangement (Remote/Hybrid/On-site), priority, and date.
   - In-place quick status dropdown updates with Fetch API.
   - Pagination and responsive table & card layout.

4. **Interview Pipeline Orchestration**
   - Manage multiple rounds (e.g. Screening, System Design, Coding, Hiring Manager Panel).
   - Video meeting URLs, calendar timestamps, preparation notes, questions to ask, and post-interview feedback.

5. **Follow-up Radar & Agenda**
   - Categorized task view: Overdue, Due Today, Upcoming, and Completed.
   - In-app follow-up completion toggle.

6. **Calendar View**
   - Chronological agenda grouping interviews and action items day-by-day.

7. **Telemetry & Conversion Analytics**
   - Real database calculations for Funnel conversion:
     - Application-to-Interview rate
     - Interview-to-Offer rate
     - Overall offer conversion rate
     - Rejection rate
     - Work arrangement distribution
     - Channel attribution (LinkedIn, Referrals, etc.)

8. **Offline Data Portability**
   - Export all user records to CSV at any time.

---

## 🎨 Design System (Adapted from Sanity.io)

- **Color Palette**: Obsidian Void (`#0b0b0b`), Card Surface (`#121214`), High-voltage Orange Accent (`#fc4404`), Tech Cyan (`#38bdf8`), Neon Mint (`#4ade80`).
- **Typography**: Editorial modern sans-serif (`Plus Jakarta Sans`) paired with technical monospace metadata (`IBM Plex Mono`).
- **Signatures**: Sticky glassmorphism navigation, high-contrast monospace badges, 3-button CTA row, and restrained 1px faint border lines.
- See [`DESIGN.md`](./DESIGN.md) for full token details.

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. (Optional) Seed Sample Demo Data
```bash
python manage.py seed_demo_data
```
> This creates a pre-populated demo account:
> - **Username:** `demo`
> - **Password:** `demo1234`

### 5. Start the Local Server
```bash
python manage.py runserver 8000
```
Open your browser to: **`http://127.0.0.1:8000/`**

---

## 🧪 Automated Testing

Run the full Django test suite (covers registration, CRUD, status changes, data isolation, search, metrics, and empty states):
```bash
python manage.py test
```

---

## 📦 Deployment Instructions (Render.com / Supabase / Railway)

### Render.com Key Vault Environment Variables
Configure the following 12 keys in your Render Dashboard / Environment Variables:

| Variable | Description | Example / Default |
|---|---|---|
| `ALLOWED_HOSTS` | Comma-separated allowed domain names | `localhost,127.0.0.1,.onrender.com,ai-learning-tracker.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string (Render Postgres or Supabase Postgres) | `postgresql://postgres:pass@db.xyz.supabase.co:5432/postgres` |
| `DEBUG` | Enable/disable debug mode in production | `False` |
| `HEALTHCHECK_ADMIN_USERNAME` | Superuser username verified by health checks | `admin` |
| `HEALTHCHECK_APPLICATION_URL` | Deployed URL (auto-adds to ALLOWED_HOSTS & CSRF origins) | `https://ai-learning-tracker.onrender.com` |
| `HEALTHCHECK_TIME_ZONE` | Time zone for operational reports & scheduling | `UTC` (or `Asia/Kolkata`, `America/New_York`) |
| `PYTHON_VERSION` | Python runtime version for Render buildpacks | `3.14.0` |
| `REDIS_URL` | Redis instance URL for high-speed cache & session storage | `redis://red-xxxx:6379` |
| `SECRET_KEY` | Production Django cryptographic secret key | `your-production-secret-key-here` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role API key | `eyJhbGciOi...` |
| `SUPABASE_STORAGE_BUCKET` | Supabase storage bucket name for attachments | `resumes` |
| `SUPABASE_URL` | Supabase project API URL | `https://xyz.supabase.co` |

### Health Check Endpoint
Render Health Check Path: `/health/` or `/healthcheck/`
- Validates database connectivity, cache/Redis status, admin user existence, and Supabase storage readiness.

### Production Build & Start Commands (Render.com)
**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```bash
python manage.py runserver 0.0.0.0:$PORT
```
*(Or with gunicorn/uvicorn: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`)*
