from fastapi import APIRouter
from tareas_recurrentes import generar_pagos_pendientes

router = APIRouter()

@router.get("/tareas/generar-pagos")
def ejecutar_generacion_pagos():
    """
    Endpoint para ser llamado por Vercel Cron Jobs.
    Ejecutará la misma función que antes estaba en APScheduler.
    """
    try:
        generar_pagos_pendientes()
        return {"mensaje": "Tarea ejecutada correctamente"}
    except Exception as e:
        return {"error": str(e)}
