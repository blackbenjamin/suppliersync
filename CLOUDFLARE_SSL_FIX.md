# Cloudflare SSL/TLS Configuration for Vercel

## Problem: SSL Handshake Failed

This error occurs when Cloudflare's SSL/TLS mode is incompatible with Vercel's SSL certificate.

## Solution: Configure Cloudflare SSL/TLS Mode

### Step 1: Check DNS Records

1. Go to Cloudflare Dashboard → Your Domain → DNS
2. Verify you have a CNAME record:
   - **Name**: `projects` (or `@` if using root domain)
   - **Target**: `cname.vercel-dns.com` (or your Vercel-assigned CNAME)
   - **Proxy status**: 🟠 Proxied (orange cloud)

### Step 2: Configure SSL/TLS Mode

**Critical**: Cloudflare SSL mode must be set correctly for Vercel.

1. Go to Cloudflare Dashboard → Your Domain → SSL/TLS
2. Set **SSL/TLS encryption mode** to: **Full (strict)**
   - Not "Full" (this causes handshake failures)
   - Not "Flexible" (less secure)
   - **Must be "Full (strict)"**

### Step 3: Verify Vercel Domain Configuration

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add domain: `projects.benjaminblack.consulting`
3. Vercel will provide DNS instructions
4. Follow the CNAME record instructions

### Step 4: Wait for Propagation

- DNS changes can take 5-60 minutes
- SSL certificate provisioning can take 2-24 hours
- Check status in Vercel → Domains → Your domain

## Troubleshooting

### Error: "SSL handshake failed"

**Fix 1**: Set SSL/TLS mode to "Full (strict)" in Cloudflare
- Cloudflare Dashboard → SSL/TLS → Overview
- Change from "Full" to "Full (strict)"

**Fix 2**: Check DNS proxy status
- DNS → Your CNAME record
- Make sure it's 🟠 Proxied (orange cloud), not ⚪ DNS only (gray cloud)

**Fix 3**: Verify Vercel domain is active
- Vercel Dashboard → Settings → Domains
- Check that domain shows "Valid Configuration"
- If not, re-add the domain and follow instructions

**Fix 4**: Temporarily disable Cloudflare proxy (for testing)
- Set DNS record to ⚪ DNS only (gray cloud)
- Wait 5 minutes
- Test if site loads
- If it works, the issue is Cloudflare SSL mode - switch back to proxy and use "Full (strict)"

### Error: "Certificate not valid"

- Wait for Vercel to provision SSL certificate (can take 24 hours)
- Check Vercel → Domains → SSL status
- If pending, wait and check back later

### Error: "DNS not resolving"

- Verify CNAME points to `cname.vercel-dns.com` (or Vercel's provided target)
- Check Cloudflare DNS cache: Settings → Network → Clear cache
- Wait 5-60 minutes for DNS propagation

## Quick Checklist

- [ ] DNS CNAME record exists: `projects` → `cname.vercel-dns.com`
- [ ] DNS record is 🟠 Proxied (orange cloud)
- [ ] Cloudflare SSL/TLS mode is set to **Full (strict)**
- [ ] Domain added in Vercel → Settings → Domains
- [ ] Vercel shows "Valid Configuration" for domain
- [ ] Waited 5-60 minutes after DNS changes
- [ ] Cleared browser cache and tried again

## Still Having Issues?

1. **Check Vercel logs**: Vercel Dashboard → Deployments → Click latest → View Logs
2. **Check Cloudflare logs**: Cloudflare Dashboard → Analytics → Security Events
3. **Test DNS directly**: `dig projects.benjaminblack.consulting` (should show Vercel IPs)
4. **Test SSL**: `curl -I https://projects.benjaminblack.consulting` (should return 200)

## Alternative: Use Cloudflare DNS Only (No Proxy)

If SSL issues persist, you can use Cloudflare DNS without proxy:

1. Cloudflare → DNS → Your CNAME record
2. Click the 🟠 orange cloud → Change to ⚪ gray cloud (DNS only)
3. Wait 5 minutes
4. Test domain

**Note**: This disables Cloudflare CDN/caching but avoids SSL issues.

