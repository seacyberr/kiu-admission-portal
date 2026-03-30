# KIU Admission Portal — Deployment Guide

## Free Hosting Options (No Subscription Required)

### Option 1: PythonAnywhere (Recommended - Free MySQL)

**Steps:**
1. Sign up at https://www.pythonanywhere.com (free tier)
2. Upload your code via Git or Files tab
3. Create a MySQL database:
   - Go to Databases tab
   - Create MySQL database (free)
   - Note your credentials: `yourusername$kiu_admissions`

4. Set environment variables in `Files` tab → `.env`:
```
DATABASE_URL=mysql+pymysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$kiu_admissions
SECRET_KEY=your-generated-secret-key
CORS_ORIGINS=*
PORT=8080
BREVO_SMTP_USER=your-brevo-smtp-user
BREVO_SMTP_KEY=your-brevo-smtp-key
```

5. Install dependencies in Bash console:
```bash
cd Kiu-Admission-Portal/artifacts/flask-api
pip install -r requirements.txt
```

6. Configure Web App:
   - Go to Web tab → Add a new web app
   - Choose "Flask"
   - Set source code path
   - Set WSGI file to: `/home/yourusername/Kiu-Admission-Portal/artifacts/flask-api/wsgi.py`
   - Set working directory

7. Your app will be live at: `https://yourusername.pythonanywhere.com`

---

### Option 2: Render (Free PostgreSQL)

**Steps:**
1. Push code to GitHub
2. Sign up at https://render.com (free tier)
3. Create PostgreSQL database (free)
4. Create Web Service:
   - Connect GitHub repo
   - Build command: `cd artifacts/flask-api && pip install -r requirements.txt`
   - Start command: `cd artifacts/flask-api && gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
   - Add environment variables

---

### Option 3: Railway (Free $5 Credit)

**Steps:**
1. Push code to GitHub
2. Sign up at https://railway.app (free $5/month credit)
3. Create project from GitHub
4. Add MySQL plugin (free tier)
5. Set environment variables
6. Deploy automatically

---

## Local Development

```bash
# Install dependencies
cd Kiu-Admission-Portal/artifacts/flask-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Flask dev server
python app.py

# Or run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app
```

## Production Reverse Proxy (Nginx example)

Assumes:
- Flask API runs on `127.0.0.1:5001`
- React frontend is served as static files (or a separate service) for non-`/api` routes
- Certificate uploads are allowed up to at least `5MB` each

```nginx
server {
  listen 80;
  server_name your-domain.com;

  # Allow uploads (backend limit is 5MB per file)
  client_max_body_size 6m;

  # API: proxy everything under /api to Flask
  location /api/ {
    proxy_pass http://127.0.0.1:5001/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  # Frontend: serve built assets (example path)
  # If you serve frontend via another container/service, you can swap this for a proxy_pass.
  location / {
    root /var/www/kiu-portal/artifacts/kiu-portal/dist/public;
    try_files $uri $uri/ /index.html;
    index index.html;
  }
}
```

## Upload persistence note

The backend stores uploaded certificates on disk under:
- `artifacts/flask-api/uploads/certificates/`

In production, ensure this directory is writable and persists across restarts
(e.g., mount a persistent volume or shared storage).

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | MySQL/PostgreSQL connection string | Yes |
| `SECRET_KEY` | JWT secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`) | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | No (default: `*`) |
| `PORT` | Server port | No (default: 5001) |
| `BREVO_SMTP_USER` | Brevo SMTP login | No (for email OTP) |
| `BREVO_SMTP_KEY` | Brevo SMTP key | No (for email OTP) |