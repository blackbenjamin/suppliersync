# Fix: Railway API Returns "Not Found"

## The Problem

`curl https://your-railway-app.railway.app/api/stats` returns "Not found"

This means Railway can't find the API endpoints. Most likely: **Root directory is wrong**.

## Root Cause

Railway needs to know where your Python code is. If Railway is looking in the wrong directory, it won't find `api.py`.

## Solution: Set Railway Root Directory

### Step 1: Check Railway Service Configuration

1. **Railway Dashboard** → Your Service → **Settings** → **Service**
2. Look for **Root Directory** setting
3. **Should be**: `suppliersync` (the directory containing `api.py`)
4. **If it's blank or wrong**: Set it to `suppliersync`

### Step 2: Verify File Structure

Railway needs to see:
```
suppliersync/
  ├── api.py          ← API entry point
  ├── migrate_db.py   ← Migration script
  ├── requirements.txt
  ├── railway.json
  └── ...
```

### Step 3: Check Railway Logs

1. **Railway Dashboard** → Your Service → **Logs**
2. Look for:
   - `ModuleNotFoundError: No module named 'api'` → Root directory wrong
   - `Application startup complete` → Good!
   - `Uvicorn running on` → Good!

### Step 4: Test Railway API

After setting root directory:

1. **Test health endpoint**:
   ```bash
   curl https://your-railway-app.railway.app/health
   ```
   Should return: `{"status":"ok"}`

2. **Test stats endpoint**:
   ```bash
   curl https://your-railway-app.railway.app/api/stats
   ```
   Should return JSON (not "Not found")

## Common Issues

### Issue 1: Root Directory Not Set

**Fix**: 
1. Railway → Settings → Service → **Root Directory**
2. Set to: `suppliersync`
3. Save and redeploy

### Issue 2: Railway Looking in Wrong Place

**Check**:
- Railway → Settings → Service → **Root Directory**
- Should be: `suppliersync` (not blank, not `/`, not `dashboard`)

### Issue 3: API Not Starting

**Check Railway logs** for:
- Python errors
- Module import errors
- Port binding errors

## Quick Test

Try these endpoints:

1. **Health** (simplest):
   ```bash
   curl https://your-railway-app.railway.app/health
   ```
   - If this works → API is running, check endpoint paths
   - If this fails → Root directory or API not starting

2. **Stats**:
   ```bash
   curl https://your-railway-app.railway.app/api/stats
   ```

## Verify Railway Configuration

### Required Settings:

1. **Root Directory**: `suppliersync`
2. **Start Command**: `python migrate_db.py && uvicorn api:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**:
   - `SQLITE_PATH=/tmp/suppliersync.db`
   - `OPENAI_API_KEY=your_key`
   - `CORS_ORIGINS=https://suppliersyncdash.vercel.app`

## Still Getting "Not Found"?

1. **Check Railway logs** - what errors do you see?
2. **Check Railway service status** - is it running?
3. **Verify root directory** - is it set to `suppliersync`?
4. **Test health endpoint** - does `/health` work?

The most common fix: **Set Root Directory to `suppliersync` in Railway settings!**

