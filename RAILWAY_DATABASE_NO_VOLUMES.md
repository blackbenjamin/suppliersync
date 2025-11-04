# Railway Database Setup (Without Volumes)

## Railway Doesn't Have Volumes?

No problem! Railway can still create databases. Here are alternatives:

## Option 1: Use /tmp Directory (Simplest)

Railway always has `/tmp` available. This works, but data is lost on restart.

### Setup:

1. **Railway Dashboard** → Your Service → **Variables**
2. **Add/Update**:
   - Variable: `SQLITE_PATH`
   - Value: `/tmp/suppliersync.db`
3. **Save**
4. **Redeploy Railway**

Database will be created automatically when Railway tries to connect.

**Note**: Database is temporary - will be lost if Railway restarts. Fine for testing/demos.

## Option 2: Use Working Directory

Railway can create files in the working directory.

### Setup:

1. **Railway Dashboard** → Your Service → **Variables**
2. **Add/Update**:
   - Variable: `SQLITE_PATH`
   - Value: `suppliersync.db` (relative path, creates in working directory)
3. **Save**
4. **Redeploy Railway**

## Option 3: Check Railway Logs First

Before changing anything, check what the actual error is:

1. **Railway Dashboard** → Your Service → **Logs**
2. Look for errors like:
   - `unable to open database file`
   - `no such table: products`
   - `database not found`

The error message will tell us exactly what's wrong!

## Most Likely Issue: Database Schema Not Initialized

Even if database file exists, **tables might not exist**. Railway needs to run database migrations.

### Check if Database Initialization Runs:

1. **Railway Dashboard** → Your Service → **Logs**
2. Look for messages like:
   - `Migrating database`
   - `Database initialized`
   - `Creating tables`

### If Database Isn't Initialized:

You need to ensure migrations run. Check Railway's startup command:

1. **Railway Dashboard** → Your Service → **Settings** → **Deploy**
2. Check **Start Command**:
   - Should be: `uvicorn api:app --host 0.0.0.0 --port $PORT`
3. **Check if migrate_db.py runs anywhere**

## Quick Fix: Update Railway Start Command

If database schema isn't being created, update Railway startup:

1. **Railway Dashboard** → Your Service → **Settings** → **Deploy**
2. **Start Command** should be:
   ```bash
   python migrate_db.py && uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
3. **Save** and **Redeploy**

This ensures database schema is created before API starts.

## Recommended Setup (No Volumes):

1. **Set Environment Variable**:
   - `SQLITE_PATH=/tmp/suppliersync.db`

2. **Update Start Command** (if needed):
   - `python migrate_db.py && uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Redeploy Railway**

4. **Check Logs**:
   - Should see: `Migrating database: /tmp/suppliersync.db`
   - Should see: `Database initialized`

## Still Having Issues?

**Check Railway Logs** - they will show:
- Database path being used
- Whether database file is created
- Whether tables exist
- Exact error messages

Share the Railway logs and we can fix the exact issue!

