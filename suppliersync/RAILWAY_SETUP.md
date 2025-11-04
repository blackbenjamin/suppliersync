# Railway Configuration

Railway will auto-detect Python and use Nixpacks. To ensure it works correctly:

1. **In Railway Dashboard**:
   - Go to your service → Settings
   - Make sure "Root Directory" is set to: `suppliersync`
   - Make sure "Build Command" is empty (Nixpacks will auto-detect)
   - Make sure "Start Command" is: `uvicorn api:app --host 0.0.0.0 --port $PORT`

2. **If Railway still uses Dockerfile**:
   - Temporarily rename `Dockerfile` to `Dockerfile.backup` (already done)
   - Or in Railway Settings → Build → uncheck "Use Dockerfile"

3. **Environment Variables** (set in Railway):
   ```
   OPENAI_API_KEY=your_key_here
   SQLITE_PATH=/data/suppliersync.db
   CORS_ORIGINS=https://projects.benjaminblack.consulting
   TRUSTED_HOSTS=*
   PORT=$PORT
   ```

4. **Nixpacks should auto-detect**:
   - Python 3.9+ from `requirements.txt`
   - Install dependencies automatically
   - Run the start command

If you need to use Dockerfile instead, fix the Dockerfile by ensuring Python base image is correct.

