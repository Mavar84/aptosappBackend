import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models

# ---------------------------------------------------------
# APSCHEDULER (NO funciona en Vercel, pero NO se elimina)
# ---------------------------------------------------------
from apscheduler.schedulers.background import BackgroundScheduler
from tareas_recurrentes import generar_pagos_pendientes

# Detectar si estamos en Vercel (serverless)
EN_VERCEL = os.environ.get("VERCEL") is not None

if not EN_VERCEL:
    scheduler = BackgroundScheduler()
    scheduler.add_job(generar_pagos_pendientes, 'cron', hour=20, minute=50)
    scheduler.start()
else:
    print("⛔ APScheduler desactivado (Vercel no permite tareas en segundo plano).")

# ---------------------------------------------------------
# Importar todos los routers
# ---------------------------------------------------------
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
# Configuración de CORS
# ---------------------------------------------------------
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:19006",
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
# Crear tablas (si no existen)
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
from routes import tareas
app.include_router(tareas.router)
# ---------------------------------------------------------
# Endpoint raíz
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "mensaje": "API de Gestión de Alquileres funcionando correctamente 🚀",
        "version": "1.0.0"
    }
