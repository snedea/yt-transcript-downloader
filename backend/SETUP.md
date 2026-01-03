# Backend Setup Guide

Complete setup instructions for the YouTube Transcript Downloader backend with authentication.

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Generate JWT secret
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# 3. Run database migrations
alembic upgrade head

# 4. Start the server
uvicorn app.main:app --reload
```

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Security Configuration](#security-configuration)
3. [OAuth Setup (Optional)](#oauth-setup-optional)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Production Deployment](#production-deployment)

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# === REQUIRED ===

# OpenAI API Key (for transcript cleaning)
OPENAI_API_KEY=sk-your-key-here

# JWT Secret (MUST be unique and secure in production!)
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your-secure-random-32-byte-hex-string-here

# === OPTIONAL ===

# Environment mode (default: development)
ENVIRONMENT=development  # or 'production'

# JWT Configuration
JWT_ALGORITHM=HS256  # Default, don't change unless you know what you're doing
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Default: 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS=7  # Default: 7 days

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Database Path
DB_PATH=./data/transcripts.db

# === OAuth (if using Google/GitHub login) ===

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth Redirect Base URL
OAUTH_REDIRECT_BASE=http://localhost:3000
```

### Environment Variable Details

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for transcript cleaning |
| `JWT_SECRET_KEY` | **Critical** | See warning below | Secret key for JWT token signing |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | How long access tokens last |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | How long refresh tokens last |
| `GOOGLE_CLIENT_ID` | For Google OAuth | - | Google OAuth 2.0 Client ID |
| `GITHUB_CLIENT_ID` | For GitHub OAuth | - | GitHub OAuth App Client ID |

---

## Security Configuration

### JWT Secret Key ⚠️

**CRITICAL**: The default JWT secret is **INSECURE** and **MUST** be changed in production.

```bash
# Generate a secure secret
openssl rand -hex 32

# Add to .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

**Security Checks at Startup:**

The application will:
- ✅ Allow default secret in `development` mode (with warning)
- ❌ **Refuse to start** in `production` mode with default secret
- ❌ **Refuse to start** if secret is less than 32 characters

### Production Mode

Set `ENVIRONMENT=production` to enable:
- Strict JWT secret validation
- Enhanced security checks
- Production-optimized CORS settings

---

## OAuth Setup (Optional)

OAuth allows users to sign in with Google or GitHub. Both are optional.

### Google OAuth Setup

1. **Go to Google Cloud Console**
   https://console.cloud.google.com/

2. **Create a Project**
   - Click "Select Project" → "New Project"
   - Name it (e.g., "YouTube Transcript App")
   - Click "Create"

3. **Enable OAuth**
   - Navigate to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in application name and support email
   - Add scopes: `email`, `profile`, `openid`
   - Save

4. **Create OAuth Credentials**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - **Authorized redirect URIs**:
     ```
     http://localhost:3000/auth/callback/google
     https://yourdomain.com/auth/callback/google
     ```
   - Click "Create"

5. **Copy Credentials**
   ```bash
   GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456
   ```

6. **Update .env**
   Add the credentials to your `.env` file

### GitHub OAuth Setup

1. **Go to GitHub Settings**
   https://github.com/settings/developers

2. **Register New OAuth App**
   - Click "OAuth Apps" → "New OAuth App"
   - **Application name**: YouTube Transcript Downloader
   - **Homepage URL**: `http://localhost:3000` (or your domain)
   - **Authorization callback URL**:
     ```
     http://localhost:3000/auth/callback/github
     ```
   - Click "Register application"

3. **Generate Client Secret**
   - Click "Generate a new client secret"
   - Copy both Client ID and Client Secret immediately

4. **Copy Credentials**
   ```bash
   GITHUB_CLIENT_ID=Iv1.abc123def456
   GITHUB_CLIENT_SECRET=abc123def456ghi789jkl012mno345
   ```

5. **Update .env**
   Add the credentials to your `.env` file

### OAuth Redirect Configuration

The `OAUTH_REDIRECT_BASE` variable should match your frontend URL:

**Development:**
```bash
OAUTH_REDIRECT_BASE=http://localhost:3000
```

**Production:**
```bash
OAUTH_REDIRECT_BASE=https://yourdomain.com
```

---

## Database Setup

### Initialize Database

```bash
cd backend

# Run all migrations
alembic upgrade head
```

This creates:
- Authentication tables (`users`, `oauth_accounts`, `refresh_tokens`)
- Transcript cache table with composite primary key
- System user for orphaned transcripts

### Verify Database

```bash
# Check migration status
alembic current
# Should show: 003_composite_pk (head)

# Inspect tables
sqlite3 data/transcripts.db ".tables"
# Should show: oauth_accounts, refresh_tokens, transcripts, users

# Check schema
sqlite3 data/transcripts.db ".schema users"
```

### Migration Guide

For detailed migration instructions, troubleshooting, and rollback procedures, see:
📖 **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**

---

## Running the Application

### Development Mode

```bash
# Set environment
export ENVIRONMENT=development
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export OPENAI_API_KEY=sk-your-key-here

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Startup

You should see:
```
INFO: Using default JWT_SECRET_KEY in development mode.
      Generate a production secret with: openssl rand -hex 32
INFO: OpenAI API key validated successfully

Application starting in DEVELOPMENT mode...
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Generate unique JWT secret (32+ characters)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production CORS origins
- [ ] Run database migrations
- [ ] Set up HTTPS/reverse proxy (Caddy, nginx)
- [ ] Configure OAuth redirect URLs for production domain
- [ ] Set up monitoring/logging
- [ ] Create database backups

### Production Environment File

```bash
# .env.production
ENVIRONMENT=production

# Security (REQUIRED)
JWT_SECRET_KEY=<generated-with-openssl-rand-hex-32>
OPENAI_API_KEY=sk-prod-key-here

# CORS (Update with your domain)
CORS_ORIGINS=https://yourdomain.com

# OAuth (Production URLs)
OAUTH_REDIRECT_BASE=https://yourdomain.com
GOOGLE_CLIENT_ID=prod-google-client-id
GOOGLE_CLIENT_SECRET=prod-google-secret
GITHUB_CLIENT_ID=prod-github-client-id
GITHUB_CLIENT_SECRET=prod-github-secret

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### systemd Service (Example)

Create `/etc/systemd/system/yt-transcript-backend.service`:

```ini
[Unit]
Description=YouTube Transcript Downloader Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/yt-transcript-downloader/backend
Environment="PATH=/var/www/yt-transcript-downloader/venv/bin"
EnvironmentFile=/var/www/yt-transcript-downloader/backend/.env.production
ExecStart=/var/www/yt-transcript-downloader/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable yt-transcript-backend
sudo systemctl start yt-transcript-backend
sudo systemctl status yt-transcript-backend
```

### Reverse Proxy (Caddy Example)

```caddy
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/refresh` | POST | Get new access token |
| `/api/auth/me` | GET | Get current user info |
| `/api/auth/logout` | POST | Revoke refresh token |
| `/api/auth/logout-all` | POST | Revoke all user tokens |
| `/api/auth/oauth/{provider}` | GET | Get OAuth login URL |
| `/api/auth/oauth/callback/{provider}` | POST | OAuth callback handler |

---

## Security Features

This backend implements:

✅ **JWT Authentication** with access & refresh tokens
✅ **Refresh token rotation** (old token revoked on refresh)
✅ **Token revocation** via database blacklist
✅ **OAuth account linking** with Google & GitHub
✅ **Secure password hashing** with bcrypt
✅ **Composite primary keys** for multi-user data isolation
✅ **Production startup validation** (won't start with insecure config)

---

## Troubleshooting

### "CRITICAL: Using default JWT_SECRET_KEY in production!"

**Solution:**
```bash
export JWT_SECRET_KEY=$(openssl rand -hex 32)
# Or add to .env file
```

### "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### "Database is locked"

**Solution:**
```bash
# Stop the backend server, then run migrations
systemctl stop yt-transcript-backend
alembic upgrade head
systemctl start yt-transcript-backend
```

### OAuth "redirect_uri_mismatch"

**Solution:**
- Ensure `OAUTH_REDIRECT_BASE` matches your frontend URL
- Update OAuth provider's authorized redirect URIs
- For Google: https://console.cloud.google.com/
- For GitHub: https://github.com/settings/developers

---

## Getting Help

- **Migration issues**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **API documentation**: http://localhost:8000/docs
- **Security audit**: Check startup logs for warnings

## Next Steps

1. ✅ Complete this setup guide
2. 📱 Configure frontend authentication (see frontend README)
3. 🔒 Test authentication flows
4. 🚀 Deploy to production

---

**Security Note**: Never commit `.env` files to version control! Add `.env` to `.gitignore`.
