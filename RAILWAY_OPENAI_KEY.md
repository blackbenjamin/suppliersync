# Fix: OpenAI API Key Missing in Railway

## The Problem

Railway logs show:
```
ValueError: OPENAI_API_KEY environment variable is not set
```

This happens when trying to run orchestration. The API endpoints work, but orchestration requires OpenAI API key.

## Solution: Set OpenAI API Key in Railway

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Copy your API key (or create a new one if needed)
3. Keep it secure!

### Step 2: Set Environment Variable in Railway

1. **Railway Dashboard** → Your Service → **Variables**
2. Click **Add Variable** (or **New Variable**)
3. Set:
   - **Variable**: `OPENAI_API_KEY`
   - **Value**: `sk-your-actual-api-key-here` (your OpenAI API key)
4. Click **Save**

### Step 3: Redeploy Railway

After setting the variable:
1. Railway should auto-redeploy
2. Or manually redeploy: Railway → Deployments → Redeploy
3. Wait for deployment to complete

### Step 4: Verify

After redeploy, check Railway logs:
- Should NOT see: `OPENAI_API_KEY environment variable is not set`
- Should see: `Application startup complete`

### Step 5: Test Orchestration

Test that orchestration works:

```bash
curl -X POST https://web-production-40a43.up.railway.app/orchestrate
```

Should return JSON with orchestration results (not an error).

## Important Security Notes

### ✅ DO:
- Set `OPENAI_API_KEY` in Railway Variables (secure)
- Use Railway's environment variable system
- Keep your API key secret

### ❌ DON'T:
- Commit API keys to git
- Share API keys publicly
- Hardcode API keys in code

## Verify It's Working

After setting `OPENAI_API_KEY` and redeploying:

1. **Test orchestration**:
   ```bash
   curl -X POST https://web-production-40a43.up.railway.app/orchestrate
   ```

2. **Check stats** (should show events after orchestration):
   ```bash
   curl https://web-production-40a43.up.railway.app/api/stats
   ```

3. **Check dashboard** - should show:
   - Active SKUs: 20 ✅
   - Price events (after running orchestration)
   - CX events
   - Metrics data

## Quick Checklist

- [ ] Set `OPENAI_API_KEY` in Railway Variables
- [ ] Redeploy Railway
- [ ] Check Railway logs - no OpenAI errors
- [ ] Test orchestration endpoint
- [ ] Verify dashboard shows data

## After Setting OpenAI Key

Once `OPENAI_API_KEY` is set:
1. **Run orchestration** from dashboard or via curl
2. **Dashboard will populate** with:
   - Price events
   - CX events
   - Metrics data
   - Rejected prices (if any)

Your dashboard should be fully functional after this!

