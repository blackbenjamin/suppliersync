# RAG Functionality - Optional Feature

## Current Status

RAG (Retrieval Augmented Generation) is **optional** and currently **disabled** in Railway to avoid build timeouts.

The dashboard will automatically **hide the RAG section** if RAG is not available.

## Why RAG is Optional

RAG dependencies are heavy:
- `chromadb` - Downloads binary dependencies
- `sentence-transformers` - Downloads ML models (~100MB+)
- `langchain` - Large dependency tree

These can cause Railway build timeouts (15-20 minute limit).

## Current Behavior

✅ **Dashboard hides RAG section** if RAG is unavailable  
✅ **API returns graceful "not_available" status**  
✅ **No errors or warnings** - just silently hidden

## How to Enable RAG (Optional)

If you want to enable RAG functionality:

### Option 1: Use Full Requirements File

1. **Railway Dashboard** → Your Service → **Settings** → **Variables**
2. Check which requirements file is being used
3. Railway uses `requirements-core.txt` by default (lightweight)
4. To use full requirements, you'd need to update `nixpacks.toml` or Railway config

**Note**: This may cause build timeouts. Railway has a 15-20 minute build limit.

### Option 2: Install RAG Dependencies Manually

1. **Railway Dashboard** → Your Service → **Settings** → **Deploy**
2. Check if you can add a custom build step
3. Add: `pip install chromadb sentence-transformers langchain langchain-community`

**Note**: This will significantly increase build time.

### Option 3: Keep RAG Disabled (Recommended)

**Current setup is fine** - RAG is optional. The dashboard works perfectly without it:
- ✅ All core functionality works
- ✅ Stats, catalog, events all load
- ✅ Orchestration works
- ✅ Metrics work
- ✅ No errors or warnings

## Recommendation

**Keep RAG disabled** unless you specifically need it. The system works great without it!

## If You Need RAG

If you really need RAG functionality:

1. **Update `suppliersync/nixpacks.toml`**:
   ```toml
   [phases.install]
   cmds = [
     "python3 -m venv /opt/venv",
     "/opt/venv/bin/pip install --upgrade pip setuptools wheel",
     "/opt/venv/bin/pip install --no-cache-dir -r requirements.txt"  # Use full requirements
   ]
   ```

2. **Redeploy Railway** - Be patient, build will take 15-20 minutes

3. **Ensure documents exist**: Make sure `data/docs/` directory has files in Railway

4. **Rebuild vectorstore**: Call `/rag/rebuild` endpoint after deployment

## Current Setup is Perfect

The dashboard automatically:
- ✅ Hides RAG section when unavailable
- ✅ Shows all other data correctly
- ✅ No errors or warnings
- ✅ Clean, professional UI

**No action needed** - everything works great as-is!

