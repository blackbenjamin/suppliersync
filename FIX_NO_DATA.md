# Fix: No Data Loading + 500 Errors

## The Problem

- Dashboard shows "Loading..." but no data
- `/rag-status` returns 500 error
- Other API routes likely failing too

## Root Cause

**`ORCHESTRATOR_API_URL` is not set in Vercel**, so API routes are trying to connect to `http://localhost:8000` instead of your Railway API.

## Solution: Set Environment Variable in Vercel

### Step 1: Get Your Railway API URL

1. Go to Railway Dashboard → Your Service
2. Click on your service
3. Find the **Public Domain** or **URL** (e.g., `https://suppliersync-api.up.railway.app`)
4. Copy this URL

### Step 2: Set Environment Variable in Vercel

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Click **Add New**
3. Set:
   - **Key**: `ORCHESTRATOR_API_URL`
   - **Value**: `https://your-railway-app.railway.app` (your actual Railway URL)
   - **Environment**: All (Production, Preview, Development)
4. Click **Save**

### Step 3: Redeploy Vercel

**Important**: Environment variables are only loaded on deployment!

1. Go to **Deployments** tab
2. Click **"..."** on latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete (~2-3 minutes)

### Step 4: Verify It's Working

1. Refresh https://suppliersyncdash.vercel.app/
2. Open Browser DevTools → **Console** tab
3. Look for log messages like:
   - `[Stats] Fetching from: https://your-railway-app.railway.app/api/stats`
   - `[Catalog] Fetching from: https://your-railway-app.railway.app/api/catalog`
4. Check for data loading

## Check Vercel Logs

To see what's happening:

1. Vercel Dashboard → Your Project → **Deployments**
2. Click on latest deployment
3. Click **View Logs**
4. Look for:
   - `[Stats] Fetching from: ...` (should show Railway URL, not localhost)
   - Error messages if Railway is unreachable

## Check Railway Logs

To see if Railway is receiving requests:

1. Railway Dashboard → Your Service → **Logs**
2. Look for incoming requests
3. Check for errors

## Common Issues

### Issue 1: Still Getting 500 Errors

**Check**: Is Railway API running?
- Railway Dashboard → Service status should be "Running"
- Test Railway API directly: `curl https://your-railway-app.railway.app/health`

### Issue 2: Environment Variable Not Taking Effect

**Fix**: 
- Make sure you **redeployed** after setting the variable
- Check that variable is set for **all environments** (Production, Preview, Development)
- Verify variable name is exactly `ORCHESTRATOR_API_URL` (case-sensitive)

### Issue 3: Railway API Returns Errors

**Check Railway logs** for:
- Database connection errors
- Missing environment variables in Railway
- Python errors

### Issue 4: No Data in Database

**Fix**: Database might be empty
- Run orchestration: `curl -X POST https://your-railway-app.railway.app/orchestrate`
- Or initialize database with products

## Quick Checklist

- [ ] `ORCHESTRATOR_API_URL` set in Vercel (with your Railway URL)
- [ ] Variable set for **all environments** (Production, Preview, Development)
- [ ] **Redeployed** Vercel after setting variable
- [ ] Railway API is running (check Railway Dashboard)
- [ ] Railway API accessible (`curl https://your-railway-app.railway.app/health`)
- [ ] Checked Vercel logs for error messages
- [ ] Checked Railway logs for errors

## Testing

After setting `ORCHESTRATOR_API_URL` and redeploying:

1. Visit: `https://suppliersyncdash.vercel.app/stats`
   - Should return JSON: `{"active_skus": 20, ...}`

2. Visit: `https://suppliersyncdash.vercel.app/catalog`
   - Should return JSON array of products

3. Check browser console:
   - Should show log messages with Railway URL (not localhost)
   - No 500 errors

## Still Not Working?

1. **Share Vercel logs** (Deployments → View Logs)
2. **Share Railway logs** (Railway → Logs)
3. **Test Railway API directly**: `curl https://your-railway-app.railway.app/health`

The improved error handling will now show better error messages in the logs!

