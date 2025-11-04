# Quick Diagnostic Guide: Dashboard Not Loading Data

## Immediate Diagnostic Steps

### 1. Check Browser Console (Most Important!)

1. Open https://suppliersyncdash.vercel.app/
2. Press F12 (or Cmd+Option+I on Mac)
3. Go to **Console** tab
4. Look for errors - they will tell you exactly what's wrong

**Common errors you might see:**
- `Failed to fetch` → API URL not set or Railway API down
- `CORS policy` → CORS not configured in Railway
- `NetworkError` → API URL incorrect

### 2. Check Network Tab

1. Open DevTools → **Network** tab
2. Refresh the page
3. Look for requests to `/stats`, `/catalog`, etc.
4. Click on each request → Check:
   - **Status**: Should be 200 (green)
   - **Response**: Should show JSON data
   - **Preview**: Should show actual data

### 3. Test Next.js API Routes Directly

Open these URLs in your browser:
- `https://suppliersyncdash.vercel.app/stats`
- `https://suppliersyncdash.vercel.app/catalog`

**Expected**: Should show JSON data like:
```json
{"active_skus": 20, "approved_price_events": 0, ...}
```

**If you see HTML or 404**: Routes aren't working - check Vercel deployment

### 4. Check Vercel Environment Variables

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. **Verify `ORCHESTRATOR_API_URL` is set**:
   ```
   ORCHESTRATOR_API_URL=https://your-railway-app.railway.app
   ```
   **Important**: 
   - Must include `https://`
   - Must be your actual Railway URL
   - No trailing slash

3. **After setting/changing**: Click "Redeploy" → "Redeploy" latest deployment

### 5. Test Railway API Directly

Replace `your-railway-app.railway.app` with your actual Railway URL:

```bash
# Test health endpoint
curl https://your-railway-app.railway.app/health

# Test stats endpoint  
curl https://your-railway-app.railway.app/api/stats

# Test catalog endpoint
curl https://your-railway-app.railway.app/api/catalog
```

**Expected**: Should return JSON data

**If fails**: Railway API is down or URL is wrong

### 6. Check Railway Logs

1. Go to Railway Dashboard → Your Service → **Logs**
2. Look for errors, especially:
   - Database connection errors
   - Missing environment variables
   - Python errors

### 7. Check Railway Environment Variables

1. Railway Dashboard → Your Service → **Variables**
2. Verify these are set:
   ```
   OPENAI_API_KEY=your_key_here
   SQLITE_PATH=/data/suppliersync.db
   CORS_ORIGINS=https://suppliersyncdash.vercel.app
   ```

## Most Common Issues & Fixes

### Issue: "Failed to fetch" in Console

**Cause**: `ORCHESTRATOR_API_URL` not set in Vercel

**Fix**:
1. Vercel → Settings → Environment Variables
2. Add: `ORCHESTRATOR_API_URL=https://your-railway-app.railway.app`
3. Redeploy

### Issue: CORS Error

**Cause**: Railway CORS not configured

**Fix**:
1. Railway → Variables → Add: `CORS_ORIGINS=https://suppliersyncdash.vercel.app`
2. Redeploy Railway

### Issue: API Returns Empty Arrays

**Cause**: Database is empty

**Fix**:
1. Check Railway logs for database errors
2. Database might need initialization - run orchestration or populate script

### Issue: 500 Errors

**Cause**: Railway API has an error

**Fix**:
1. Check Railway logs for error details
2. Verify all environment variables are set
3. Check database connection

## Quick Fix Checklist

- [ ] Set `ORCHESTRATOR_API_URL` in Vercel (must include `https://`)
- [ ] Set `CORS_ORIGINS` in Railway (must include your Vercel URL)
- [ ] Redeploy both Vercel and Railway after changing env vars
- [ ] Test Railway API directly with curl
- [ ] Check browser console for specific errors
- [ ] Check Vercel deployment logs
- [ ] Check Railway service logs

## Still Not Working?

1. **Share browser console errors** - they will tell us exactly what's wrong
2. **Share Network tab** - shows which requests are failing
3. **Check Railway URL** - verify it's correct and accessible
4. **Check Vercel logs** - Deployment → Latest → View Logs

