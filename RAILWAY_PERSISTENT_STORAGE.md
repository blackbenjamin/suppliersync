# Railway Persistent Database Storage

## The Problem

By default, Railway uses **ephemeral filesystems** - data is lost on every redeployment. Your SQLite database gets wiped each time Railway redeploys.

## Solution: Railway Persistent Volumes

Railway offers **persistent volumes** that retain data across deployments.

## Step-by-Step Setup

### Step 1: Create a Persistent Volume in Railway

1. **Railway Dashboard** → Your Service → **Settings** → **Volumes**
2. Click **+ New Volume**
3. Configure:
   - **Name**: `database` (or any name you prefer)
   - **Mount Path**: `/data` (this is where the volume will be mounted)
   - **Size**: Start with `1GB` (you can increase later)
4. Click **Create**

### Step 2: Set Database Path Environment Variable

1. **Railway Dashboard** → Your Service → **Variables**
2. Add/Update:
   - **Variable**: `SQLITE_PATH`
   - **Value**: `/data/suppliersync.db`
3. Click **Save**

This ensures the database is stored in the persistent volume at `/data/suppliersync.db`.

### Step 3: Verify Volume is Mounted

After redeploying, check Railway logs:
```
INFO: Application startup complete
```

The database should now persist at `/data/suppliersync.db` in the persistent volume.

### Step 4: Redeploy

Railway will automatically redeploy when you:
- Add a volume
- Update environment variables

Wait for deployment to complete.

## Verify It's Working

After redeploy:

1. **Run orchestration** to create some data:
   ```bash
   curl -X POST https://your-railway-app.railway.app/orchestrate
   ```

2. **Check stats** - should show data:
   ```bash
   curl https://your-railway-app.railway.app/api/stats
   ```

3. **Redeploy Railway** (trigger a new deployment)

4. **Check stats again** - data should still be there! ✅

## Important Notes

### ✅ Do:
- Store database in `/data/` (persistent volume)
- Use `SQLITE_PATH=/data/suppliersync.db` environment variable
- Create volume BEFORE setting `SQLITE_PATH` (or set both together)

### ❌ Don't:
- Store database in `/app/` or `/tmp/` (ephemeral)
- Use default `suppliersync.db` path (lost on redeploy)
- Forget to set `SQLITE_PATH` environment variable

## Current Configuration

After setup, your Railway config should have:

**Environment Variables:**
- `SQLITE_PATH=/data/suppliersync.db`
- `OPENAI_API_KEY=sk-...` (your key)
- `CORS_ORIGINS=...` (your dashboard URL)
- `TRUSTED_HOSTS=*` (or specific hosts)

**Volume:**
- Name: `database` (or your choice)
- Mount Path: `/data`
- Size: `1GB` (increase if needed)

## Troubleshooting

### Database Still Losing Data?

1. **Check volume mount**: Railway logs should show volume mounted
2. **Verify SQLITE_PATH**: Make sure it's set to `/data/suppliersync.db`
3. **Check file location**: Database should be at `/data/suppliersync.db` in volume
4. **Verify volume exists**: Railway → Settings → Volumes → Should see your volume

### Database Not Found Errors?

1. **Ensure migration runs**: `migrate_db.py` should create database if missing
2. **Check file permissions**: Volume should be writable
3. **Verify SQLITE_PATH**: Should match volume mount path

### Volume Not Appearing?

1. **Redeploy after creating volume**: Railway needs to redeploy to mount volume
2. **Check Railway logs**: Should show volume mounted
3. **Verify mount path**: Should be `/data` (or your chosen path)

## Migration Scripts

The migration and populate scripts already respect `SQLITE_PATH`:

- `migrate_db.py` uses `os.getenv("SQLITE_PATH", "suppliersync.db")`
- `populate_inventory.py` uses `os.getenv("SQLITE_PATH", "suppliersync.db")`
- `api.py` uses `os.getenv("SQLITE_PATH", "suppliersync.db")`

So once `SQLITE_PATH=/data/suppliersync.db` is set, everything will use the persistent volume automatically!

## Summary

1. ✅ Create persistent volume at `/data`
2. ✅ Set `SQLITE_PATH=/data/suppliersync.db` environment variable
3. ✅ Redeploy Railway
4. ✅ Verify data persists across deployments

Your database will now survive redeployments! 🎉

