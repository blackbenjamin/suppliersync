# Deployment Guide

This guide covers deploying SupplierSync to GitHub and hosting it on Vercel with Cloudflare DNS.

## Prerequisites

- GitHub account
- Vercel account (connect with GitHub)
- Cloudflare account (for DNS management)
- Domain: `benjaminblack.consulting` configured in Cloudflare

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web UI

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `suppliersync` (or your preferred name)
3. **Description**: "Multi-Agent AI Orchestrator for E-Commerce - Supplier Management, Dynamic Pricing, and CX Optimization"
4. **Visibility**: Select **Public** ✅
5. **Initialize**:
   - ✅ Add a README (optional, we already have one)
   - ✅ Add .gitignore (optional, we already have one)
   - ✅ Choose a license (MIT recommended)
6. **Click "Create repository"**

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if you don't have it
# brew install gh  # macOS
# gh auth login

# Create repository
cd /Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo
gh repo create suppliersync --public --description "Multi-Agent AI Orchestrator for E-Commerce" --source=. --remote=origin --push
```

## Step 2: Push Code to GitHub

```bash
# Navigate to project directory
cd /Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo

# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Multi-Agent AI Orchestrator with security, testing, and documentation"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/suppliersync.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Configure Repository for Public Sharing

### Add Topics/Tags (for discoverability)

1. Go to your repository on GitHub
2. Click the gear icon (⚙️) next to "About"
3. Add topics:
   - `ai`
   - `multi-agent`
   - `llm`
   - `fastapi`
   - `nextjs`
   - `e-commerce`
   - `pricing`
   - `supplier-management`
   - `python`
   - `typescript`

### Add Repository Description

Update the repository description to:
"Production-ready multi-agent AI system for supplier management, dynamic pricing, and customer experience optimization. Features governance rules, RAG, security hardening, and comprehensive testing."

### Add Website Link

In repository settings → Pages (if applicable), add:
- Website: `https://projects.benjaminblack.consulting`

## Step 4: Deploy Dashboard to Vercel

### Option A: Deploy via Vercel Dashboard

1. **Go to Vercel**: https://vercel.com/new
2. **Import Git Repository**:
   - Select your GitHub repository
   - Click "Import"
3. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
4. **Environment Variables**:
   Add the following:
   ```
   ORCHESTRATOR_API_URL=https://suppliersync-api.railway.app
   SQLITE_PATH=/tmp/suppliersync.db
   ```
   (We'll set up the API separately - see Step 5)
5. **Click "Deploy"**

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to dashboard directory
cd dashboard

# Deploy
vercel

# Follow prompts:
# - Link to existing project? (No)
# - Project name: suppliersync-dashboard
# - Directory: ./
# - Override settings: (No)
# - Environment variables: Add ORCHESTRATOR_API_URL
```

### Configure Custom Domain

1. **In Vercel Dashboard**:
   - Go to your project → Settings → Domains
   - Add domain: `projects.benjaminblack.consulting`
   - Click "Add"

2. **Vercel will provide DNS records**:
   - CNAME: `projects.benjaminblack.consulting` → `cname.vercel-dns.com`
   - Or A record instructions

## Step 5: Deploy API Service

The Python FastAPI service needs to run separately. Options:

### Option A: Railway (Recommended)

1. **Go to Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Select repository** → **Deploy**
4. **Configure**:
   - Root Directory: `suppliersync`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_key_here
   SQLITE_PATH=/data/suppliersync.db
   CORS_ORIGINS=https://projects.benjaminblack.consulting
   TRUSTED_HOSTS=*
   ```
6. **Get deployment URL**: `https://your-app.railway.app`
7. Update `ORCHESTRATOR_API_URL` in Vercel dashboard

### Option B: Render

1. **Go to Render**: https://render.com
2. **New Web Service** → **Connect GitHub**
3. **Configure**:
   - Name: `suppliersync-api`
   - Root Directory: `suppliersync`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**: Same as above
5. **Get URL**: `https://suppliersync-api.onrender.com`

### Option C: Fly.io (Alternative)

```bash
# Install flyctl
brew install flyctl

# Login
flyctl auth login

# Launch app
cd suppliersync
flyctl launch

# Follow prompts, then:
flyctl deploy
```

## Step 6: Configure Cloudflare DNS

1. **Log into Cloudflare**: https://dash.cloudflare.com
2. **Select domain**: `benjaminblack.consulting`
3. **Go to DNS** → **Records**
4. **Add CNAME record**:
   - **Type**: CNAME
   - **Name**: `projects`
   - **Target**: `cname.vercel-dns.com` (or the value from Vercel)
   - **Proxy status**: ✅ Proxied (orange cloud)
   - **TTL**: Auto
5. **Click "Save"**

### SSL/TLS Settings

1. **Go to SSL/TLS** → **Overview**
2. **Encryption mode**: Full (strict)
3. **Always Use HTTPS**: On
4. **Automatic HTTPS Rewrites**: On

## Step 7: Update Environment Variables

### Vercel (Dashboard)

1. Go to project → Settings → Environment Variables
2. Update:
   ```
   ORCHESTRATOR_API_URL=https://your-api-url.railway.app
   SQLITE_PATH=/tmp/suppliersync.db
   ```

### API Service (Railway/Render)

Update:
```
CORS_ORIGINS=https://projects.benjaminblack.consulting,https://www.projects.benjaminblack.consulting
TRUSTED_HOSTS=your-api-url.railway.app,projects.benjaminblack.consulting
```

## Step 8: Verify Deployment

### Check Dashboard

1. Visit: `https://projects.benjaminblack.consulting`
2. Should load the Next.js dashboard
3. Check browser console for errors

### Check API

1. Visit: `https://your-api-url.railway.app/health`
2. Should return: `{"status": "ok"}`

### Test Integration

1. Open dashboard
2. Click "Run Orchestration"
3. Check that API calls work

## Step 9: Add to Portfolio Website

### Update Personal Website

Add a project card linking to:
- **Live Demo**: `https://projects.benjaminblack.consulting`
- **GitHub**: `https://github.com/YOUR_USERNAME/suppliersync`

### Example Portfolio Entry

```markdown
## SupplierSync - Multi-Agent AI Orchestrator

**Technologies**: Python, FastAPI, Next.js, OpenAI, SQLite, LangChain

**Description**: Production-ready multi-agent AI system for supplier management, dynamic pricing, and customer experience optimization.

**Features**:
- Multi-agent orchestration (Supplier, Buyer, CX agents)
- Governance rules and policy enforcement
- RAG (Retrieval Augmented Generation)
- Security hardening and comprehensive testing
- Real-time dashboard with metrics and observability

**Live Demo**: [projects.benjaminblack.consulting](https://projects.benjaminblack.consulting)
**GitHub**: [View Source](https://github.com/YOUR_USERNAME/suppliersync)
```

## Troubleshooting

### Dashboard Not Loading

- Check Vercel deployment logs
- Verify environment variables are set
- Check that API URL is correct
- Verify CORS settings in API

### API Not Responding

- Check Railway/Render logs
- Verify environment variables
- Check that database is accessible
- Verify OpenAI API key is set

### DNS Not Resolving

- Wait 24-48 hours for DNS propagation
- Check Cloudflare DNS settings
- Verify SSL/TLS settings
- Try clearing DNS cache: `sudo dscacheutil -flushcache` (macOS)

### CORS Errors

- Update `CORS_ORIGINS` in API to include your domain
- Check that API returns proper CORS headers
- Verify that requests are going to correct API URL

## Production Checklist

Before going live:

- [ ] All environment variables set
- [ ] API service deployed and accessible
- [ ] Dashboard deployed and accessible
- [ ] Custom domain configured
- [ ] SSL/TLS enabled (Full/Strict)
- [ ] CORS configured correctly
- [ ] Database initialized (if needed)
- [ ] OpenAI API key configured
- [ ] Rate limiting configured
- [ ] Error handling verified
- [ ] Monitoring/logging set up (optional)
- [ ] Backup strategy in place (optional)

## Cost Estimates

### Vercel (Dashboard)
- **Free tier**: Perfect for portfolio projects
- Includes: Unlimited deployments, custom domains, SSL

### Railway (API)
- **Free tier**: $5/month credit
- **Hobby plan**: ~$5-10/month

### Render (API - Alternative)
- **Free tier**: Available (with limitations)
- **Starter**: ~$7/month

### Cloudflare
- **Free**: DNS management, CDN, SSL

**Total**: ~$5-10/month for the API service

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code
3. ✅ Deploy dashboard to Vercel
4. ✅ Deploy API to Railway/Render
5. ✅ Configure Cloudflare DNS
6. ✅ Update portfolio website
7. ✅ Share with potential employers!

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Cloudflare DNS](https://developers.cloudflare.com/dns)
- [GitHub Pages](https://pages.github.com)

