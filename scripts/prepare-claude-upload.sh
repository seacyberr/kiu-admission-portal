#!/bin/bash
# Script to prepare essential project files for Claude upload
# Copies 20 key files to claude-upload/ folder

UPLOAD_DIR="claude-upload"

echo "🚀 Preparing files for Claude upload..."

# Create upload directory
mkdir -p "$UPLOAD_DIR"

# Backend files (Flask API)
echo "📁 Copying backend files..."
cp apps/flask-api/app.py "$UPLOAD_DIR/backend-app.py"
cp apps/flask-api/models.py "$UPLOAD_DIR/backend-models.py"
cp apps/flask-api/routes/auth.py "$UPLOAD_DIR/backend-routes-auth.py"
cp apps/flask-api/routes/admission.py "$UPLOAD_DIR/backend-routes-admission.py"
cp apps/flask-api/routes/career.py "$UPLOAD_DIR/backend-routes-career.py"
cp apps/flask-api/config.py "$UPLOAD_DIR/backend-config.py"
cp apps/flask-api/requirements.txt "$UPLOAD_DIR/backend-requirements.txt"
cp apps/flask-api/data/seed-programs.json "$UPLOAD_DIR/backend-seed-programs.json"
cp apps/flask-api/migrations/env.py "$UPLOAD_DIR/backend-migrations-env.py"

# Frontend files (React)
echo "📁 Copying frontend files..."
cp apps/kiu-portal/src/App.tsx "$UPLOAD_DIR/frontend-App.tsx"
cp apps/kiu-portal/src/pages/home.tsx "$UPLOAD_DIR/frontend-pages-home.tsx"
cp apps/kiu-portal/src/pages/auth/login.tsx "$UPLOAD_DIR/frontend-pages-auth-login.tsx"
cp apps/kiu-portal/src/pages/auth/register.tsx "$UPLOAD_DIR/frontend-pages-auth-register.tsx"
cp apps/kiu-portal/src/pages/auth/verify-otp.tsx "$UPLOAD_DIR/frontend-pages-auth-verify-otp.tsx"
cp apps/kiu-portal/src/pages/applicant/apply.tsx "$UPLOAD_DIR/frontend-pages-applicant-apply.tsx"
cp apps/kiu-portal/src/components/layout.tsx "$UPLOAD_DIR/frontend-components-layout.tsx"
cp apps/kiu-portal/src/services/api.ts "$UPLOAD_DIR/frontend-services-api.ts"
cp apps/kiu-portal/package.json "$UPLOAD_DIR/frontend-package.json"

# Documentation
echo "📁 Copying documentation..."
cp README.md "$UPLOAD_DIR/README.md"
cp DEPLOYMENT.md "$UPLOAD_DIR/DEPLOYMENT.md"
cp IMPLEMENTATION_PLAN.md "$UPLOAD_DIR/IMPLEMENTATION_PLAN.md"

echo ""
echo "✅ Successfully copied 20 files to $UPLOAD_DIR/"
echo ""
echo "📋 Files ready for upload:"
ls -1 "$UPLOAD_DIR/"
echo ""
echo "💡 Tip: You can now zip this folder or upload files directly to Claude"