#!/usr/bin/env bash
# ==============================================================================
# Render.com Build & Deployment Script for JobTrack
# ==============================================================================
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Provisioning Key Vault Users (kanishkan & preetha)..."
python manage.py setup_production_users

echo "==> Build and user provisioning complete!"
