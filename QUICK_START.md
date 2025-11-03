# Quick Start Guide - GitHub & Deployment

## 🚀 Quick Steps to Deploy

### 1. Create GitHub Repository (5 minutes)

```bash
# Navigate to project
cd /Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Multi-Agent AI Orchestrator"

# Create public repository on GitHub
gh repo create suppliersync --public --description "Multi-Agent AI Orchestrator for E-Commerce" --source=. --remote=origin --push

# Or manually on GitHub.com:
# 1. Go to https://github.com/new
# 2. Repository name: suppliersync
# 3. Visibility: Public ✅
# 4. Create repository
# 5. Then: git remote add origin https://github.com/YOUR_USERNAME/suppliersync.git
# 6. git push -u origin main
```

### 2. Deploy Dashboard to Vercel (5 minutes)

**Option A: Via Web UI**
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - Root Directory: `dashboard`
   - Framework: Next.js
4. Add environment variable:
   - `ORCHESTRATOR_API_URL` (we'll set this after deploying API)
5. Deploy!

**Option B: Via CLI**
```bash
cd dashboard
npm i -g vercel
vercel
# Follow prompts
```

### 3. Deploy API to Railway (5 minutes)

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. Configure:
   - Root Directory: `suppliersync`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   ```
   OPENAI_API_KEY=your_key_here
   SQLITE_PATH=/data/suppliersync.db
   CORS_ORIGINS=https://projects.benjaminblack.consulting
   ```
6. Copy the deployment URL

### 4. Configure Custom Domain (5 minutes)

**In Vercel:**
1. Project → Settings → Domains
2. Add: `projects.benjaminblack.consulting`

**In Cloudflare:**
1. DNS → Records
2. Add CNAME:
   - Name: `projects`
   - Target: `cname.vercel-dns.com` (or value from Vercel)
   - Proxy: ✅ (orange cloud)

### 5. Update Environment Variables

**In Vercel:**
- Update `ORCHESTRATOR_API_URL` to your Railway API URL

**In Railway:**
- Update `CORS_ORIGINS` to include your domain

### 6. Verify Everything Works

1. Visit: `https://projects.benjaminblack.consulting`
2. Should see the dashboard
3. Test "Run Orchestration" button

## 📝 Important Notes

### For Public Repository

- ✅ Remove any sensitive data before pushing
- ✅ Use `.env.example` files (already done)
- ✅ Don't commit `.env` files (already in `.gitignore`)
- ✅ Add clear README (already done)
- ✅ Add license (MIT recommended)

### For Deployment

- **Dashboard**: Free on Vercel
- **API**: Free tier on Railway (~$5/month credit)
- **DNS**: Free on Cloudflare
- **Total Cost**: ~$0-5/month

### Environment Variables Needed

**Vercel (Dashboard):**
- `ORCHESTRATOR_API_URL` - Your Railway API URL

**Railway (API):**
- `OPENAI_API_KEY` - Your OpenAI API key
- `SQLITE_PATH` - `/data/suppliersync.db` (or `/tmp/suppliersync.db`)
- `CORS_ORIGINS` - `https://projects.benjaminblack.consulting`
- `TRUSTED_HOSTS` - `*` (or specific hosts)

## 🎯 Next Steps After Deployment

1. **Add to Portfolio**: Update your personal website with project link
2. **Share on LinkedIn**: Post about your project
3. **Update README**: Add live demo link
4. **Add Badges**: Add deployment status badges

## 🔗 Useful Links

- **GitHub**: https://github.com/YOUR_USERNAME/suppliersync
- **Live Demo**: https://projects.benjaminblack.consulting
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard
- **Cloudflare Dashboard**: https://dash.cloudflare.com

## ❓ Troubleshooting

**Dashboard not loading?**
- Check Vercel deployment logs
- Verify environment variables
- Check API URL is correct

**API not responding?**
- Check Railway logs
- Verify OpenAI API key
- Check CORS settings

**DNS not working?**
- Wait 24-48 hours for propagation
- Check Cloudflare DNS settings
- Verify SSL/TLS settings

Need help? Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

