from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models
from apscheduler.schedulers.background import BackgroundScheduler
from tareas_recurrentes import generar_pagos_pendientes

scheduler = BackgroundScheduler()
scheduler.add_job(generar_pagos_pendientes, 'cron', hour=12, minute=24)
scheduler.start()

# Importar todos los routers
from routes import (
    apartamentos,
    inquilinos,
    contratos,
    pagos,
    devoluciones,
    fotos
)
# nuevos
from routes import usuarios, auth
# ---------------------------------------------------------
# Inicialización de la aplicación FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title="Sistema de Gestión de Alquileres",
    description="API REST para administración de apartamentos, contratos, inquilinos, pagos y devoluciones.",
    version="1.0.0"
)

# ---------------------------------------------------------
# Configuración de CORS (para permitir conexión desde Expo o React)
# ---------------------------------------------------------
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite/React
    "http://localhost:19006", # Expo
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Crear las tablas en Supabase (si no existen)
# ---------------------------------------------------------
try:
    print("Creando tablas en Supabase (si no existen)...")
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("⚠️ Error creando tablas:", e)

# ---------------------------------------------------------
# Registrar los routers
# ---------------------------------------------------------
app.include_router(apartamentos.router)
app.include_router(inquilinos.router)
app.include_router(contratos.router)
app.include_router(pagos.router)
app.include_router(devoluciones.router)
app.include_router(fotos.router)
# nuevos
app.include_router(usuarios.router)
app.include_router(auth.router)
# ---------------------------------------------------------
# Endpoint raíz (verificación)
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "mensaje": "API de Gestión de Alquileres funcionando correctamente 🚀",
        "version": "1.0.0"
    }
