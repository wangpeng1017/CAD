# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AI-powered CAD drawing compliance checker for GB/T 14665-2012 standards.

**Tech Stack:**
- Backend: Python 3.11+ with FastAPI, ezdxf for CAD parsing
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS
- Deployment: Docker, Kubernetes (Leaflow), Cloudflare Tunnel

## Common Commands

### Development

**Start services (recommended):**
```powershell
.\start.ps1
```

**Manual startup:**

Backend:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```powershell
cd frontend
npm run dev
```

**System health check:**
```powershell
.\check_system.ps1
```

### Docker

```powershell
docker-compose up --build
docker-compose up -d  # background
docker-compose down
```

### Testing

**Backend:**
```bash
cd backend
pytest tests/
```

**DWG conversion test:**
```powershell
python backend/test_dwg_converter.py path/to/file.dwg
```

**Create test DXF files:**
```powershell
python create_test_dxf.py          # Basic test
python create_advanced_test_dxf.py # Advanced test
python debug_analysis.py backend/uploads/test_sample.dxf
```

**Frontend:**
```bash
cd frontend
npm test
npm run lint
```

### Production Deployment

**Build & push Docker images (via GitHub Actions):**
```bash
git push origin main  # Triggers .github/workflows/deploy.yml
```

**Deploy to Kubernetes:**
```bash
kubectl apply -f k8s/leaflow-deploy-complete.yml
```

**With Cloudflare Tunnel:**
```powershell
.\start-with-tunnel.ps1
```

## Architecture

### Backend Structure

- **`app/main.py`** - FastAPI entry point with CORS, routes registration
- **`app/config.py`** - Application settings (Pydantic)
- **`app/api/`** - API route handlers:
  - `upload.py` - File upload (DXF/DWG)
  - `analysis.py` - Background analysis tasks
  - `report.py` - Report generation & export
- **`app/services/`** - Business logic:
  - `dxf_parser.py` - Parse DXF files with ezdxf
  - `dwg_converter.py` - DWG→DXF conversion (ODA/ezdxf/LibreDWG)
  - `compliance_checker.py` - Rule checking engine
- **`app/models/schemas.py`** - Pydantic data models
- **`config/rules_gbt14665.yaml`** - GB/T 14665-2012 rule definitions

### Frontend Structure

- **`app/page.tsx`** - Main upload interface
- **`app/report/[id]/page.tsx`** - Report display with real-time polling
- **`components/FileUpload.tsx`** - Drag-drop file upload component
- **`lib/api.ts`** - Backend API client
- **`types/index.ts`** - TypeScript types matching backend models

### Analysis Workflow

1. **Upload** → File saved to `backend/uploads/` with UUID
2. **Convert** (if DWG) → Try ezdxf → ODA Converter → LibreDWG
3. **Parse** → Extract layers, entities, dimensions, texts (ezdxf)
4. **Check** → Apply rules from `rules_gbt14665.yaml`:
   - Layer placement (Table 6)
   - Lineweights (Table 1)
   - Colors (Table 2)
   - Text heights (Table 3)
   - Dimension consistency (Section 6.3)
5. **Report** → Calculate compliance score, generate violations list
6. **Export** → JSON/HTML/PDF formats

### State Management

**Phase 1 (Current):** In-memory storage in `analysis.py`
- `analysis_results = {}` dict keyed by analysis_id
- Cleared on backend restart

**Phase 2 (Planned):** Database persistence (Redis/PostgreSQL)

## Key Patterns

### Error Handling

- All API endpoints return structured errors via FastAPI `HTTPException`
- DWG conversion failures return user-friendly messages with manual conversion instructions
- File validation happens before processing (size, extension)

### Async Processing

- File analysis runs in background tasks (`BackgroundTasks`)
- Frontend polls `/api/v1/analyze/{id}` for status updates
- Status: `pending` → `processing` → `completed` | `failed`

### Rule Configuration

Edit `backend/config/rules_gbt14665.yaml` to adjust:
- Expected layer names
- Lineweight thresholds & tolerances
- Font height ranges
- Dimension consistency thresholds

### CORS Configuration

Update `app/main.py` to add allowed origins:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-domain.com",
]
```

## Environment Variables

### Backend (.env)

```env
DEBUG=true
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=dxf,dwg
ANALYSIS_TIMEOUT=60
ODA_CONVERTER_PATH=  # Optional: C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe
TEMP_DIR=./temp
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker Compose (.env for cloudflared)

```env
CLOUDFLARE_TUNNEL_TOKEN=your_token_here
```

## Common Issues

### DWG Files Not Converting

- System defaults to ezdxf (limited DWG support)
- For better compatibility: Install [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)
- Configure path in `.env`: `ODA_CONVERTER_PATH=...`
- Or manually convert DWG→DXF in AutoCAD before upload

### Frontend Build Fails in Docker

- `next.config.ts` has `typescript.ignoreBuildErrors: true` for CI/CD speed
- For local development, fix TypeScript errors properly
- Check `NEXT_PUBLIC_API_URL` environment variable is set

### CORS Errors

- Verify frontend URL is in `app/main.py` CORS `allow_origins` list
- For Docker: Use service names (`http://backend:8000`)
- For Kubernetes: Update Ingress paths in `k8s/ingress.yml`

### Analysis Timeout

- Increase `ANALYSIS_TIMEOUT` in backend `.env`
- Default: 30s (sufficient for <10MB files)
- For large files: 60s recommended

## Development Workflow

1. **New Feature:**
   - Backend: Add route in `app/api/`, logic in `app/services/`
   - Frontend: Create component in `components/`, update `lib/api.ts`
   - Types: Update `backend/app/models/schemas.py` & `frontend/types/index.ts`

2. **New Rule:**
   - Add to `config/rules_gbt14665.yaml`
   - Implement checker in `services/compliance_checker.py`
   - Add violation type to `models/schemas.py` if needed

3. **Testing:**
   - Create test DXF with `create_test_dxf.py`
   - Debug analysis with `debug_analysis.py`
   - Check system health with `check_system.ps1`

## Deployment

### Local Access URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production (Kubernetes)

- Frontend/Backend: https://cad-wangpeng.leaflow.net
- Ingress routes:
  - `/` → frontend:3000
  - `/api` → backend:8000
  - `/docs` → backend:8000

### Cloudflare Tunnel

- Configure tunnel token in `.env`
- Start with: `docker-compose up -d`
- Tunnel connects `frontend:3000` to public domain
- See `QUICK_START_NO_MSI.md` for setup

## Important Notes

- **File Storage:** Temporary uploads are NOT persisted across restarts
- **Phase 1 Limitations:** No database, no user authentication, in-memory state
- **DWG Support:** Limited; recommend converting to DXF manually
- **Concurrency:** Phase 1 optimized for <10 concurrent users
- **Phase 2 Planned:** Shapely geometry engine, CV models, database persistence
- **Phase 3 Planned:** LLM-driven semantic analysis (Gemini API)

## Useful Scripts

- `start.ps1` - Interactive startup wizard
- `start-with-tunnel.ps1` - Start with Cloudflare tunnel
- `check_system.ps1` - System health diagnostics
- `debug_analysis.py` - Debug DXF analysis pipeline
- `create_test_dxf.py` - Generate test files
- `backend/test_dwg_converter.py` - Test DWG conversion

## Standards Reference

- **GB/T 14665-2012:** Chinese CAD drafting standards
- Rules defined in YAML: layers, lineweights, colors, fonts, dimensions
- See `prd.md` for full product requirements
