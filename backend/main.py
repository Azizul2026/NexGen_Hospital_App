from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from core.database import db
from services.seed import seed_all

# ✅ ROUTERS
from routers import auth, admin, doctor, patient, ai


# ─────────────────────────────────────────────
# 🔹 LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("nexgen")


# ─────────────────────────────────────────────
# 🔹 STARTUP / SHUTDOWN
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏥 NexGen Hospital starting...")

    try:
        db.connect()
        seed_all()   # ✅ IMPORTANT (creates admin user on Render)
        logger.info("✅ Database connected & seeded")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

    # 🔥 IMPORTANT FOR RENDER
    port = os.environ.get("PORT", "10000")
    logger.info(f"🚀 Running on port {port}")

    yield

    db.close()
    logger.info("👋 NexGen Hospital stopped")


# ─────────────────────────────────────────────
# 🔹 APP
# ─────────────────────────────────────────────
app = FastAPI(
    title="NexGen Hospital API",
    description="Hospital Management System with AI + Analytics + Security",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ─────────────────────────────────────────────
# 🔐 SECURITY HEADERS
# ─────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"   # ✅ allows docs
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ─────────────────────────────────────────────
# 🌍 CORS (FIXED FOR VERCEL)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nex-gen-hospital-app.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─────────────────────────────────────────────
# 🔗 ROUTERS
# ─────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doctor.router)
app.include_router(patient.router)
app.include_router(ai.router)


# ─────────────────────────────────────────────
# 📁 OPTIONAL FRONTEND SERVING
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

if os.path.isdir(FRONTEND_DIR):

    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    js_path = os.path.join(FRONTEND_DIR, "js")
    if os.path.isdir(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")

    def serve(page):
        return FileResponse(os.path.join(FRONTEND_DIR, page))

    @app.get("/")
    def root():
        return serve("index.html")

    @app.get("/login.html")
    def login():
        return serve("login.html")

    @app.get("/admin.html")
    def admin_page():
        return serve("admin.html")

    @app.get("/doctor.html")
    def doctor_page():
        return serve("doctor.html")

    @app.get("/patient.html")
    def patient_page():
        return serve("patient.html")


# ─────────────────────────────────────────────
# ❤️ HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "NexGen Hospital API",
        "version": "3.0.0"
    }


# ─────────────────────────────────────────────
# ℹ️ SYSTEM INFO
# ─────────────────────────────────────────────
@app.get("/info")
def info():
    return {
        "name": "NexGen Hospital System",
        "version": "3.0.0",
        "features": [
            "JWT Authentication",
            "Refresh Tokens",
            "Admin Dashboard",
            "Doctor Portal",
            "Patient Portal",
            "AI Disease Prediction",
            "Risk Scoring",
            "ICU Prediction",
            "Revenue Analytics",
            "AI Forecasting",
            "Security Hardening"
        ]
    }
