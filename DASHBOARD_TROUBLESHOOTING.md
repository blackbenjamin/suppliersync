# Dashboard Data Loading Troubleshooting Guide

## Problem: Dashboard Shows "Loading..." But No Data

This guide helps diagnose and fix issues where the dashboard loads but shows no data.

## Step 1: Check Browser Console

1. Open https://suppliersyncdash.vercel.app/
2. Open Browser DevTools (F12 or Cmd+Option+I)
3. Go to **Console** tab
4. Look for errors:
   - Network errors (failed fetch requests)
   - CORS errors
   - API errors

**Common errors to look for:**
- `Failed to fetch` → API URL incorrect or API not accessible
- `CORS policy` → CORS not configured correctly
- `404` → API route not found
- `500` → Server error

## Step 2: Check Network Tab

1. Open Browser DevTools → **Network** tab
2. Refresh the page
3. Look for failed requests:
   - `/stats` → Should return stats data
   - `/catalog` → Should return catalog data
   - `/price-events` → Should return price events
   - `/rejected-prices` → Should return rejected prices
   - `/cx-events` → Should return CX events
   - `/rag-status` → Should return RAG status

**Check each request:**
- Status code (should be 200)
- Response body (should contain JSON data)
- Request URL (should be correct)

## Step 3: Verify Environment Variables

### In Vercel Dashboard:

1. Go to Vercel → Your Project → Settings → Environment Variables
2. Verify these are set:
   ```
   ORCHESTRATOR_API_URL=https://your-railway-app.railway.app
   ```
   **Important**: Must include `https://` protocol

3. **Redeploy** after changing environment variables:
   - Go to Deployments → Click "..." → Redeploy

### Check Railway API is Running:

1. Open Railway Dashboard → Your Service
2. Check logs for errors
3. Test API directly:
   ```
   curl https://your-railway-app.railway.app/health
   ```
   Should return: `{"status":"ok"}`

## Step 4: Test API Endpoints Directly

### Test Railway API:

```bash
# Test health endpoint
curl https://your-railway-app.railway.app/health

# Test stats endpoint
curl https://your-railway-app.railway.app/api/stats

# Test catalog endpoint
curl https://your-railway-app.railway.app/api/catalog
```

**Expected responses:**
- `/health` → `{"status":"ok"}`
- `/api/stats` → `{"active_skus": 20, "approved_price_events": 0, ...}`
- `/api/catalog` → `{"products": [...]}`

### Test Next.js API Routes:

Visit these URLs directly in browser:
- `https://suppliersyncdash.vercel.app/stats`
- `https://suppliersyncdash.vercel.app/catalog`
- `https://suppliersyncdash.vercel.app/price-events`

**Expected**: Should return JSON data (not HTML)

## Step 5: Check CORS Configuration

### In Railway Dashboard:

1. Go to Variables tab
2. Verify `CORS_ORIGINS` includes:
   ```
   CORS_ORIGINS=https://suppliersyncdash.vercel.app,https://projects.benjaminblack.consulting
   ```

3. If missing, add it and redeploy

### Test CORS:

```bash
# Test CORS headers
curl -H "Origin: https://suppliersyncdash.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://your-railway-app.railway.app/api/stats

# Should return CORS headers:
# Access-Control-Allow-Origin: https://suppliersyncdash.vercel.app
```

## Step 6: Check Database Initialization

The API needs data in the database to return results.

### Check if Database Has Data:

```bash
# SSH into Railway (if possible) or check logs
# Database should be initialized with products

# Or run a test orchestration to generate data:
curl -X POST https://your-railway-app.railway.app/orchestrate
```

### Initialize Database:

If database is empty, you need to:
1. Run `populate_inventory.py` script (via Railway console or locally)
2. Or trigger an orchestration run to generate data

## Step 7: Common Issues and Fixes

### Issue 1: "Failed to fetch" in Console

**Cause**: API URL incorrect or API not accessible

**Fix**:
1. Check `ORCHESTRATOR_API_URL` in Vercel is correct
2. Verify Railway API is running (check Railway logs)
3. Test Railway API URL directly in browser

### Issue 2: CORS Errors

**Cause**: CORS not configured in Railway

**Fix**:
1. Add `CORS_ORIGINS` to Railway Variables
2. Include your Vercel domain
3. Redeploy Railway service

### Issue 3: 404 Errors on API Routes

**Cause**: Next.js API routes not working

**Fix**:
1. Check that route files exist in `dashboard/app/(api)/`
2. Check Vercel build logs for errors
3. Verify routes are exported correctly

### Issue 4: Empty Arrays Returned

**Cause**: Database is empty

**Fix**:
1. Initialize database with products
2. Run orchestration to generate events
3. Check Railway logs for database errors

### Issue 5: API Returns 500 Errors

**Cause**: Server-side error in API

**Fix**:
1. Check Railway logs for error details
2. Verify environment variables are set
3. Check database connection

## Step 8: Debugging Checklist

- [ ] Browser console shows no errors
- [ ] Network tab shows successful API calls (200 status)
- [ ] Railway API `/health` endpoint works
- [ ] `ORCHESTRATOR_API_URL` is set in Vercel
- [ ] `CORS_ORIGINS` includes Vercel domain in Railway
- [ ] Database has data (products, events)
- [ ] Railway service is running (not crashed)
- [ ] Vercel deployment succeeded (check Deployments tab)

## Step 9: Quick Test Script

Create a test HTML file to debug:

```html
<!DOCTYPE html>
<html>
<head>
  <title>API Test</title>
</head>
<body>
  <h1>API Test</h1>
  <button onclick="testAPI()">Test API</button>
  <pre id="result"></pre>
  
  <script>
    async function testAPI() {
      const API_URL = 'https://your-railway-app.railway.app';
      const resultEl = document.getElementById('result');
      
      try {
        // Test health
        const health = await fetch(`${API_URL}/health`);
        resultEl.textContent += `Health: ${await health.text()}\n`;
        
        // Test stats
        const stats = await fetch(`${API_URL}/api/stats`);
        resultEl.textContent += `Stats: ${await stats.text()}\n`;
        
        // Test catalog
        const catalog = await fetch(`${API_URL}/api/catalog`);
        resultEl.textContent += `Catalog: ${await catalog.text()}\n`;
      } catch (error) {
        resultEl.textContent += `Error: ${error.message}\n`;
      }
    }
  </script>
</body>
</html>
```

## Step 10: Enable Detailed Logging

### Add Logging to API Routes:

Check Railway logs for detailed error messages:
1. Railway Dashboard → Your Service → Logs
2. Look for errors, warnings, or stack traces
3. Check Vercel logs: Vercel Dashboard → Deployments → View Logs

## Still Not Working?

1. **Check Railway logs** for server-side errors
2. **Check Vercel logs** for build/deployment errors
3. **Test API directly** using curl or Postman
4. **Verify database** has data (if empty, initialize it)
5. **Check network** - ensure Railway API is accessible

## Quick Fixes Summary

1. **Set `ORCHESTRATOR_API_URL`** in Vercel environment variables
2. **Set `CORS_ORIGINS`** in Railway environment variables
3. **Redeploy both services** after changing env vars
4. **Initialize database** with products if empty
5. **Check Railway API** is running and accessible

