# Deployment Documentation

## Deployment Platform

**Live Application:** https://project-4-karting-121d969fb7d5.herokuapp.com/

**Platform:** Heroku  
**Database:** PostgreSQL (Heroku Postgres)  
**Region:** Europe (eu-west-1)  
**Dyno Type:** Basic  

## Prerequisites

### Required Accounts
1. **Heroku Account** - https://signup.heroku.com/
2. **GitHub Account** - https://github.com/
3. **PostgreSQL** - Provided by Heroku addon

### Required Software
```bash
# Heroku CLI
brew install heroku/brew/heroku  # macOS
# or
curl https://cli-assets.heroku.com/install.sh | sh  # Linux

# Git
git --version  # Verify Git installed

# Python 3.9+
python3 --version
```

## Environment Configuration

### Environment Variables Required

Create a `.env` file for local development (NEVER commit this file):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (local development uses SQLite, leave blank)
DATABASE_URL=

# Heroku Production Variables (set via Heroku dashboard)
# Do NOT put these in .env file
```

### Production Environment Variables (Heroku)

Set these via Heroku dashboard or CLI:

```bash
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="project-4-karting-121d969fb7d5.herokuapp.com"
heroku config:set DATABASE_URL="postgres://..." # Auto-set by Heroku Postgres
heroku config:set DISABLE_COLLECTSTATIC=1  # Initial deployment only
```

## Deployment Steps

### 1. Prepare Application

**Create requirements.txt:**
```bash
pip freeze > requirements.txt
```

**Verify Procfile exists:**
```bash
cat Procfile
# Should contain:
# web: gunicorn kartcontrol.wsgi --log-file -
```

**Create runtime.txt:**
```bash
echo "python-3.9.18" > runtime.txt
```

### 2. Configure Django Settings

**Update settings/production.py:**

```python
import os
import dj_database_url

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Create Heroku Application

```bash
# Login to Heroku
heroku login

# Create new application
heroku create project-4-karting

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Verify database created
heroku config:get DATABASE_URL
```

### 4. Deploy Application

**Option A: Deploy via Heroku CLI**

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial deployment"

# Add Heroku remote
heroku git:remote -a project-4-karting

# Deploy to Heroku
git push heroku main
```

**Option B: Deploy via GitHub Integration**

1. Go to Heroku Dashboard
2. Select your app → Deploy tab
3. Choose "GitHub" as deployment method
4. Connect to your GitHub repository
5. Enable "Automatic Deploys" from main branch
6. Click "Deploy Branch"

### 5. Run Migrations

```bash
# Apply database migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Collect static files (if needed)
heroku run python manage.py collectstatic --noinput
```

### 6. Verify Deployment

```bash
# Open application in browser
heroku open

# View logs
heroku logs --tail

# Check dyno status
heroku ps

# Run Django checks
heroku run python manage.py check --deploy
```

## Post-Deployment Configuration

### 1. Create Initial Data

```bash
# Create track via Django admin
heroku open /admin

# Login with superuser credentials
# Navigate to Sessions → Tracks
# Create single track instance
```

### 2. Create Kart Fleet

```bash
# Via Django admin or shell
heroku run python manage.py shell

>>> from karts.models import Kart
>>> for i in range(1, 11):
...     Kart.objects.create(number=i, status='ACTIVE')
>>> exit()
```

### 3. Verify Security

```bash
# Run Django deployment checks
heroku run python manage.py check --deploy

# Verify SSL
curl -I https://project-4-karting-121d969fb7d5.herokuapp.com

# Check security headers
curl -I https://project-4-karting-121d969fb7d5.herokuapp.com | grep -i "strict-transport-security"
```

## Continuous Deployment

### Automatic Deployments (Recommended)

1. Connect Heroku app to GitHub repository
2. Enable automatic deploys from `main` branch
3. Every push to `main` triggers deployment
4. Heroku runs tests before deploying (if configured)

### Manual Deployments

```bash
# Deploy specific branch
git push heroku feature-branch:main

# Rollback to previous version
heroku rollback

# View release history
heroku releases
```

## Troubleshooting

### Common Issues

**1. Application Error (500)**

```bash
# Check logs
heroku logs --tail

# Common causes:
# - Missing environment variables
# - Database not migrated
# - Static files not collected
```

**Fix:**
```bash
heroku config  # Verify all env vars set
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
```

**2. Database Connection Error**

```bash
# Verify DATABASE_URL set
heroku config:get DATABASE_URL

# Reset database (CAUTION: Deletes all data)
heroku pg:reset DATABASE
heroku run python manage.py migrate
```

**3. Static Files Not Loading**

```bash
# Disable collectstatic during deployment
heroku config:set DISABLE_COLLECTSTATIC=1

# Manually collect static files
heroku run python manage.py collectstatic --noinput

# Re-enable collectstatic
heroku config:unset DISABLE_COLLECTSTATIC
```

**4. SECRET_KEY Error**

```bash
# Generate new secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set on Heroku
heroku config:set SECRET_KEY="generated-key-here"
```

### Useful Heroku Commands

```bash
# View application logs
heroku logs --tail

# Access Django shell
heroku run python manage.py shell

# Run management commands
heroku run python manage.py <command>

# Restart dynos
heroku restart

# Scale dynos
heroku ps:scale web=1

# Access database
heroku pg:psql

# Database backups
heroku pg:backups:capture
heroku pg:backups:download
```

## Database Management

### Backups

```bash
# Create manual backup
heroku pg:backups:capture

# Schedule automatic backups (requires paid plan)
heroku pg:backups:schedule DATABASE_URL --at '02:00 UTC'

# List backups
heroku pg:backups

# Download backup
heroku pg:backups:download
```

### Restore Database

```bash
# Restore from latest backup
heroku pg:backups:restore

# Restore from specific backup
heroku pg:backups:restore b001
```

## Monitoring

### Heroku Metrics

```bash
# View metrics
heroku metrics:web

# View dyno status
heroku ps
```

### Application Logs

```bash
# Real-time logs
heroku logs --tail

# Filter logs
heroku logs --source app
heroku logs --dyno web.1

# Download logs
heroku logs -n 1500 > logs.txt
```

## Security Checklist

Before production deployment:

- [x] DEBUG = False
- [x] SECRET_KEY in environment variable (not in code)
- [x] ALLOWED_HOSTS configured
- [x] SECURE_SSL_REDIRECT = True
- [x] SESSION_COOKIE_SECURE = True
- [x] CSRF_COOKIE_SECURE = True
- [x] SECURE_HSTS_SECONDS = 31536000
- [x] Database uses SSL
- [x] No secrets in git repository
- [x] .env in .gitignore
- [x] CSRF protection enabled
- [x] XSS protection enabled

## Cost Optimization

**Current Setup:**
- Basic Dyno: $7/month
- Mini PostgreSQL: $5/month
- **Total: $12/month**

**Free Tier Alternative:**
- Eco Dyno: Free (sleeps after 30min inactivity)
- Essential PostgreSQL: $0 (10k rows limit)
- **Total: $0/month**

## Summary

The KartControl application is deployed on Heroku with:

✅ **PostgreSQL database** - Production-grade data storage  
✅ **SSL encryption** - Secure HTTPS connections  
✅ **Environment-based config** - Separate dev/production settings  
✅ **Automatic deployments** - GitHub integration  
✅ **Static file serving** - WhiteNoise compression  
✅ **Database backups** - Automated backup schedule  
✅ **Security hardened** - All Django security features enabled  

The deployment is production-ready and follows industry best practices.
