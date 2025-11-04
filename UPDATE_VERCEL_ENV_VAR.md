# Update Existing Vercel Environment Variable

## The Issue

Vercel says `ORCHESTRATOR_API_URL` already exists, but it's likely set to the wrong value (`http://localhost:8000`).

## Solution: Update the Existing Variable

### Step 1: Find Your Railway API URL

1. Go to Railway Dashboard → Your Service
2. Find the **Public Domain** or **URL** 
   - Example: `https://suppliersync-api.up.railway.app`
3. Copy this URL

### Step 2: Update Environment Variable in Vercel

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Find `ORCHESTRATOR_API_URL` in the list
3. Click **Edit** (or the pencil icon)
4. **Update the Value** to your Railway URL:
   - Change from: `http://localhost:8000` (or whatever it currently is)
   - Change to: `https://your-railway-app.railway.app` (your actual Railway URL)
5. Make sure **Environment** includes: Production, Preview, Development
6. Click **Save**

### Step 3: Redeploy Vercel

**Critical**: Environment variables only load on deployment!

1. Go to **Deployments** tab
2. Click **"..."** on latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete (~2-3 minutes)

### Step 4: Verify

After redeploy, check Vercel logs:

1. **Deployments** → Latest → **View Logs**
2. Look for log messages like:
   - `[Stats] Fetching from: https://your-railway-app.railway.app/api/stats`
   - Should show your Railway URL, NOT `localhost:8000`

## What to Check

### Current Value
- In Vercel → Environment Variables → Click on `ORCHESTRATOR_API_URL`
- What does it say? If it's `http://localhost:8000`, that's the problem!

### Railway URL Format
- Must start with `https://`
- Must be your actual Railway domain (e.g., `https://suppliersync-api.up.railway.app`)
- No trailing slash

### Environment Scope
- Make sure it's set for **all environments**:
  - ✅ Production
  - ✅ Preview  
  - ✅ Development

## Still Having Issues?

### Option 1: Delete and Recreate
If you can't edit:
1. Delete the existing `ORCHESTRATOR_API_URL` variable
2. Create a new one with the correct Railway URL
3. Redeploy

### Option 2: Check Railway Service
1. Make sure Railway service is running
2. Test Railway API: `curl https://your-railway-app.railway.app/health`
3. Should return: `{"status":"ok"}`

### Option 3: Check Vercel Logs
After redeploy, check logs for:
- `[Stats] Fetching from: ...` (should show Railway URL)
- Any connection errors

## Quick Test

After updating and redeploying:

1. Visit: `https://suppliersyncdash.vercel.app/stats`
   - Should return JSON data (not error)

2. Check browser console:
   - Should see data loading
   - No 500 errors

The key is: **Update the existing variable, don't create a new one!**

