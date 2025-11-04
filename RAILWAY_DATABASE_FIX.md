# Fix: Railway API 500 Error - Database Issue

## The Problem

Railway API is returning 500 error: `"Failed to fetch stats. Check server logs for details."`

This means Railway API is running, but it can't access the database.

## Root Cause

The SQLite database doesn't exist or the path is wrong in Railway.

## Solution: Check Railway Database Configuration

### Step 1: Check Railway Environment Variables

1. Go to Railway Dashboard → Your Service → **Variables**
2. Check if `SQLITE_PATH` is set:
   - Should be something like: `/data/suppliersync.db` or `/tmp/suppliersync.db`
   - **Important**: Path must be writable by Railway

### Step 2: Check Railway Logs

1. Railway Dashboard → Your Service → **Logs**
2. Look for errors like:
   - `unable to open database file`
   - `no such table: products`
   - `database not found`

### Step 3: Common Issues & Fixes

#### Issue 1: Database Doesn't Exist

**Fix**: Database needs to be initialized. Railway needs persistent storage.

**Option A: Use Railway Volume (Recommended)**

1. Railway Dashboard → Your Service → **Settings** → **Volumes**
2. Click **Add Volume**
3. Mount path: `/data`
4. Update `SQLITE_PATH` variable to: `/data/suppliersync.db`
5. Redeploy Railway

**Option B: Use /tmp (Temporary, will be lost on restart)**

1. Set `SQLITE_PATH=/tmp/suppliersync.db`
2. Database will be created automatically
3. **Note**: Database will be lost when Railway restarts

#### Issue 2: Database Tables Don't Exist

**Fix**: Initialize database schema

1. Railway Dashboard → Your Service → **Settings** → **Deploy Logs**
2. Check if database initialization runs on startup
3. Or manually run migration:
   ```bash
   # In Railway console or via script
   python migrate_db.py
   ```

#### Issue 3: Database Path is Wrong

**Fix**: Check `SQLITE_PATH` environment variable

1. Railway → Variables → Check `SQLITE_PATH`
2. Should be absolute path like `/data/suppliersync.db`
3. Make sure directory exists (Railway creates it automatically)

### Step 4: Initialize Database Schema

The database needs tables. Railway should auto-create schema, but if not:

1. **Check if `migrate_db.py` runs on startup**
2. **Or add initialization to Railway startup**:
   - Railway → Settings → Start Command
   - Should run: `python migrate_db.py && uvicorn api:app --host 0.0.0.0 --port $PORT`

### Step 5: Populate Database with Products

If database exists but is empty:

1. **Check Railway logs** for initialization
2. **Run populate script** (if available):
   ```bash
   python populate_inventory.py
   ```
3. **Or trigger orchestration** to generate data:
   ```bash
   curl -X POST https://your-railway-app.railway.app/orchestrate
   ```

## Quick Fix: Use Railway Volume

### Recommended Setup:

1. **Railway Dashboard** → Your Service → **Settings** → **Volumes**
2. Click **Add Volume**
3. **Mount Path**: `/data`
4. **Update Environment Variable**:
   - Variable: `SQLITE_PATH`
   - Value: `/data/suppliersync.db`
5. **Redeploy Railway**

This creates persistent storage that survives restarts.

## Verify Database Exists

After fixing, check Railway logs:

1. Should see: `Database initialized` or similar
2. Or check health endpoint: `curl https://your-railway-app.railway.app/health`
3. Should return: `{"status":"ok"}`

## Check Railway Logs for Specific Error

The Railway logs will tell you exactly what's wrong:

1. Railway Dashboard → Your Service → **Logs**
2. Look for:
   - `sqlite3.OperationalError` → Database path/permission issue
   - `no such table` → Schema not initialized
   - `unable to open database file` → Path doesn't exist or not writable

## Most Common Fix

**Add Railway Volume**:
1. Railway → Settings → Volumes → Add Volume
2. Mount: `/data`
3. Set `SQLITE_PATH=/data/suppliersync.db`
4. Redeploy

The database will be created automatically when Railway tries to connect to it!

