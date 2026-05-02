"""
Vian CommandOS × Genius Brain Nursery — FastAPI Main App
포트: 5051
nginx: /vian-commandos-genius/
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.core.commandos.hud_bridge import router as hud_router
from backend.core.guard.guard_router import router as guard_router
from backend.api.local_index_router import router as local_index_router
from backend.api.local_index_router import preview_router as local_preview_router
from backend.api.audit_router import router as audit_router
from backend.api.audit_router import undo_router

app = FastAPI(
    title="Vian CommandOS × Genius Brain",
    version="2.0.0",
    root_path="/vian-commandos-genius",
)

# [의존성] 연결: Chrome Extension useCommandIntent.ts / 단독 수정 금지
# Chrome Extension에서의 localhost 호출 허용 (개발 및 로컬 운영)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5051",
        "http://localhost:5173",  # Vite dev server
        "chrome-extension://*",  # Chrome Extension 모든 ID
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hud_router)
app.include_router(guard_router)
app.include_router(local_index_router)
app.include_router(local_preview_router)
app.include_router(audit_router)
app.include_router(undo_router)

# React 프론트엔드 SPA 서빙 (빌드 후)
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    @app.get("/command-room/{path:path}")
    async def serve_spa(path: str):
        """SPA catch-all — React Router 처리."""
        index = _frontend_dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"error": "Frontend not built"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vian-commandos-genius", "port": 5051}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=5051, reload=True)
