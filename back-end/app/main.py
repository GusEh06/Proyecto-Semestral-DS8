from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth,
    reservaciones,
    admin,
    mesas,
    tipos_mesa,
    vision
)

# Importar servicio MQTT
from app.services.mqtt_service import mqtt_service

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("\n" + "=" * 60)
    print("Iniciando aplicacion FastAPI...")
    print("=" * 60)

    # Iniciar servicio MQTT
    mqtt_service.start()

    yield

    # Shutdown
    print("\n" + "=" * 60)
    print("Cerrando aplicacion...")
    mqtt_service.stop()
    print("=" * 60 + "\n")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para sistema de reservaciones de restaurante con visión artificial",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
        "health": "ok",
        "mqtt_connected": mqtt_service.connected
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "mqtt_status": "connected" if mqtt_service.connected else "disconnected"
    }
