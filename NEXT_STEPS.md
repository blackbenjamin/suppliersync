# Next Steps - Deployment Checklist

## ✅ Completed
- [x] Created GitHub repository
- [x] Pushed code to GitHub
- [x] Updated README with correct username

## 🚀 Next Steps

### Step 1: Deploy Dashboard to Vercel (5 min)

1. **Go to Vercel**: https://vercel.com/new
2. **Import Git Repository**:
   - Click "Import Git Repository"
   - Select your `suppliersync` repository
   - Click "Import"
3. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `dashboard` ⚠️ **IMPORTANT**
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)
4. **Environment Variables** (add these):
   ```
   ORCHESTRATOR_API_URL=https://your-api-url.railway.app
   ```
   ⚠️ We'll update this after deploying the API
5. **Click "Deploy"**
6. **Wait for deployment** (~2-3 minutes)
7. **Copy your deployment URL** (e.g., `suppliersync-dashboard.vercel.app`)

### Step 2: Deploy API to Railway (5 min)

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (can use GitHub)
3. **New Project** → **Deploy from GitHub repo**
4. **Select repository**: `suppliersync`
5. **Configure**:
   - **Root Directory**: `suppliersync` ⚠️ **IMPORTANT**
   - **Build Command**: Leave empty (Nixpacks will auto-detect)
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **If Railway tries to use Dockerfile**: 
     - Go to Settings → Build
     - Uncheck "Use Dockerfile" 
     - Or ensure Dockerfile is renamed to `Dockerfile.backup`
6. **Environment Variables** (click "Variables" tab):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SQLITE_PATH=/data/suppliersync.db
   CORS_ORIGINS=https://projects.benjaminblack.consulting,https://suppliersync-dashboard.vercel.app
   TRUSTED_HOSTS=*
   PORT=$PORT
   ```
7. **Wait for deployment** (~3-5 minutes)
8. **Get your API URL**:
   - Click on your service
   - Go to "Settings" → "Generate Domain"
   - Copy the URL (e.g., `suppliersync-api.railway.app`)

**Note**: Railway should auto-detect Python and use Nixpacks. If it tries to use Dockerfile and fails, see `suppliersync/RAILWAY_SETUP.md` for troubleshooting.

### Step 3: Update Environment Variables

**In Vercel:**
1. Go to your project → Settings → Environment Variables
2. Update `ORCHESTRATOR_API_URL` to your Railway API URL:
   ```
   ORCHESTRATOR_API_URL=https://suppliersync-api.railway.app
   ```
3. **Redeploy** (or wait for auto-deploy)

**In Railway:**
1. Update `CORS_ORIGINS` to include your Vercel URL:
   ```
   CORS_ORIGINS=https://projects.benjaminblack.consulting,https://suppliersync-dashboard.vercel.app
   ```

### Step 4: Configure Cloudflare DNS (5 min)

1. **Log into Cloudflare**: https://dash.cloudflare.com
2. **Select domain**: `benjaminblack.consulting`
3. **Go to DNS** → **Records**
4. **Add CNAME record**:
   - **Type**: CNAME
   - **Name**: `projects`
   - **Target**: Go to Vercel → Project → Settings → Domains
     - Add domain: `projects.benjaminblack.consulting`
     - Vercel will show you the target (e.g., `cname.vercel-dns.com`)
   - **Proxy status**: ✅ Proxied (orange cloud)
   - **TTL**: Auto
5. **Click "Save"**
6. **Wait 24-48 hours** for DNS propagation (usually faster)

### Step 5: Configure Custom Domain in Vercel

1. **In Vercel Dashboard**:
   - Go to your project → Settings → Domains
   - Click "Add Domain"
   - Enter: `projects.benjaminblack.consulting`
   - Follow instructions to verify DNS

### Step 6: Test Everything

1. **Test Dashboard**: Visit `https://projects.benjaminblack.consulting`
   - Should load the dashboard
   - Check browser console for errors

2. **Test API**: Visit `https://your-api-url.railway.app/health`
   - Should return: `{"status": "ok"}`

3. **Test Integration**:
   - Open dashboard
   - Click "Run Orchestration"
   - Check that API calls work

### Step 7: Update Portfolio Website

Add a project card to your portfolio website:

```markdown
## SupplierSync - Multi-Agent AI Orchestrator

**Technologies**: Python, FastAPI, Next.js, OpenAI, SQLite, LangChain

**Description**: Production-ready multi-agent AI system for supplier management, dynamic pricing, and customer experience optimization.

**Live Demo**: [projects.benjaminblack.consulting](https://projects.benjaminblack.consulting)
**GitHub**: [View Source](https://github.com/blackbenjamin/suppliersync)
```

## 📝 Important Notes

### Vercel Configuration
- **Root Directory**: Must be `dashboard` (not root)
- **Environment Variables**: Add `ORCHESTRATOR_API_URL` after Railway deployment

### Railway Configuration
- **Root Directory**: Must be `suppliersync` (not root)
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **OpenAI API Key**: Required for orchestration to work

### DNS Propagation
- Can take 24-48 hours (usually faster)
- Use `dig projects.benjaminblack.consulting` to check DNS
- Cloudflare proxy (orange cloud) speeds up propagation

### Troubleshooting

**Dashboard not loading?**
- Check Vercel deployment logs
- Verify root directory is `dashboard`
- Check environment variables

**API not responding?**
- Check Railway logs
- Verify start command is correct
- Check environment variables (especially `OPENAI_API_KEY`)

**CORS errors?**
- Update `CORS_ORIGINS` in Railway to include your domain
- Check API logs for CORS errors

**DNS not working?**
- Wait 24-48 hours
- Check Cloudflare DNS settings
- Verify Vercel domain configuration

## 🎉 Success!

Once everything is deployed:
- ✅ Dashboard live at `projects.benjaminblack.consulting`
- ✅ API live at Railway URL
- ✅ Everything connected and working
- ✅ Ready to share with potential employers!

## 📚 Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Cloudflare DNS**: https://developers.cloudflare.com/dns
- **Full Deployment Guide**: See `DEPLOYMENT.md`

