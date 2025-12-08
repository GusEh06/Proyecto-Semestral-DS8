from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth,
    reservaciones,
    admin,
    mesas,
    tipos_mesa,
    vision
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para sistema de reservaciones de restaurante con visión artificial",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← TEMPORAL para probar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registrar routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(reservaciones.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(mesas.router, prefix=settings.API_V1_PREFIX)
app.include_router(tipos_mesa.router, prefix=settings.API_V1_PREFIX)
app.include_router(vision.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "API de Sistema de Reservaciones",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "ok"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
