# Database Migration Guide

This guide explains how to run database migrations for the authentication and transcript caching system.

## Prerequisites

1. Python 3.8+ installed
2. All dependencies installed: `pip install -r requirements.txt`
3. Backend directory as working directory: `cd backend`

## Migration Overview

The authentication refactor includes three migrations:

1. **001_initial_auth**: Creates authentication tables (users, oauth_accounts, refresh_tokens)
2. **002_update_transcripts**: Adds user_id column to transcripts table
3. **003_composite_primary_key**: Restructures transcripts with composite PK (video_id, user_id)

## Quick Start

### For Fresh Installations (No Existing Database)

```bash
cd backend
alembic upgrade head
```

This will apply all migrations in order and create all tables.

### For Existing Installations (Upgrading)

**⚠️ IMPORTANT: Backup your database first!**

```bash
# Backup your database
cp data/transcripts.db data/transcripts.db.backup

# Check current migration state
alembic current

# Apply all pending migrations
alembic upgrade head
```

## Step-by-Step Migration Process

### 1. Check Current State

```bash
cd backend
alembic current
```

If you see `(head)`, you're already up to date. Otherwise, note the current revision.

### 2. View Migration History

```bash
alembic history
```

This shows all available migrations:
- `003_composite_pk` (Composite primary key for transcripts)
- `update_transcripts` (Add user_id to transcripts)
- `1234567890ab` (Initial auth tables)

### 3. Preview What Will Happen

**Migration 001** creates:
- `users` table
- `oauth_accounts` table
- `refresh_tokens` table

**Migration 002**:
- Adds `user_id` column to `transcripts` table (nullable)
- Creates foreign key to `users` table

**Migration 003** (**IMPORTANT**):
- Creates a system user for orphaned transcripts
- Assigns NULL `user_id` values to system user
- Recreates `transcripts` table with composite primary key `(video_id, user_id)`
- Makes `user_id` NOT NULL
- Each user can now have their own cached transcript for any video

### 4. Backup Your Database

```bash
# From project root
cp backend/data/transcripts.db backend/data/transcripts.db.backup-$(date +%Y%m%d-%H%M%S)
```

### 5. Run Migrations

```bash
cd backend
alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 1234567890ab, initial_auth
INFO  [alembic.runtime.migration] Running upgrade 1234567890ab -> update_transcripts, add_user_id_to_transcripts
Created system user: <uuid>
Assigned 42 orphaned transcripts to system user
INFO  [alembic.runtime.migration] Running upgrade update_transcripts -> 003_composite_pk, composite_primary_key_and_data_migration
Migration complete: transcripts table now uses composite primary key (video_id, user_id)
```

### 6. Verify Migration Success

```bash
# Check migration state
alembic current
# Should show: 003_composite_pk (head)

# Check database schema
sqlite3 backend/data/transcripts.db ".schema transcripts"
# Should show composite primary key
```

## Understanding Data Migration

### Orphaned Transcripts

Transcripts created before authentication are assigned to a system user:
- **Email**: `system@transcripts.local`
- **Username**: `system`
- **Status**: Active, verified

This user is created automatically during migration 003.

### Composite Primary Key Impact

**Before Migration 003:**
- Only one user could cache each video
- User B's request would overwrite User A's cached transcript

**After Migration 003:**
- Each user has their own cached transcript
- Multiple users can cache the same video independently
- Primary key is now `(video_id, user_id)` instead of just `video_id`

## Troubleshooting

### "Database is locked" Error

```bash
# Stop the backend server first
# Then run migrations
alembic upgrade head
```

### "Table already exists" Error

This likely means you're in an inconsistent state.

**Option 1: Start Fresh (Development Only)**
```bash
rm backend/data/transcripts.db
alembic upgrade head
```

**Option 2: Manual Recovery**
```bash
# Check which tables exist
sqlite3 backend/data/transcripts.db ".tables"

# If auth tables exist but alembic thinks they don't, stamp the migration
alembic stamp 003_composite_pk
```

### Migration Fails Midway

```bash
# Restore from backup
cp backend/data/transcripts.db.backup backend/data/transcripts.db

# Check migration state
alembic current

# Try migrating one step at a time
alembic upgrade +1
```

### Check System User

```bash
sqlite3 backend/data/transcripts.db "SELECT * FROM users WHERE email = 'system@transcripts.local';"
```

## Rolling Back (Advanced)

**⚠️ WARNING**: Rolling back migration 003 will **lose data** if multiple users have transcripts for the same video!

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade update_transcripts

# Rollback all migrations (DANGER!)
alembic downgrade base
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Database backup created
- [ ] Migrations tested in staging environment
- [ ] Application server will be stopped during migration
- [ ] Downtime window scheduled (estimate: 1-5 minutes depending on data size)

### Production Migration Steps

```bash
# 1. Backup
cp data/transcripts.db data/transcripts.db.backup-prod-$(date +%Y%m%d-%H%M%S)

# 2. Stop application
systemctl stop yt-transcript-backend  # or your process manager

# 3. Run migrations
cd backend
alembic upgrade head

# 4. Verify
alembic current
sqlite3 data/transcripts.db "SELECT COUNT(*) FROM users;"

# 5. Start application
systemctl start yt-transcript-backend

# 6. Test authentication endpoints
curl http://localhost:8000/api/auth/me
```

## Environment Variables

Before running migrations, ensure these are set:

```bash
# Required for app startup (not migrations)
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database location (optional, defaults to backend/data/transcripts.db)
export DB_PATH=/path/to/transcripts.db
```

## Getting Help

If migrations fail:

1. Check `alembic.log` for detailed error messages
2. Ensure database file is writable
3. Verify all dependencies are installed
4. Check SQLite version: `sqlite3 --version` (should be 3.8+)

## Next Steps

After successful migration:

1. Configure environment variables (see [SETUP.md](SETUP.md))
2. Generate secure JWT secret key
3. Configure OAuth providers (optional)
4. Start the backend server
5. Test authentication endpoints

## Reference

- Alembic documentation: https://alembic.sqlalchemy.org/
- SQLModel documentation: https://sqlmodel.tiangolo.com/
- Migration files: `backend/migrations/versions/`
