from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
import models, schemas
from security import get_current_user

router = APIRouter(
    prefix="/devoluciones",
    tags=["Devolución de Depósitos"],
    dependencies=[Depends(get_current_user)]  # 🔒 todos los endpoints requieren login
)

# ---------------------------------------------------------
# Registrar nueva devolución
# ---------------------------------------------------------
@router.post("/", response_model=schemas.DevolucionDepositoResponse)
def registrar_devolucion(devol: schemas.DevolucionDepositoCreate):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == devol.contrato_id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no existe")

            inquilino = db.query(models.Inquilino).filter(models.Inquilino.cedula == devol.inquilino_cedula).first()
            if not inquilino:
                raise HTTPException(status_code=404, detail="Inquilino no existe")

            devolucion = models.DevolucionDeposito(**devol.dict())
            db.add(devolucion)
            db.commit()
            db.refresh(devolucion)
            return devolucion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar devolución: {str(e)}")


# ---------------------------------------------------------
# Listar todas las devoluciones
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.DevolucionDepositoResponse])
def listar_devoluciones():
    try:
        with SessionLocal() as db:
            return db.query(models.DevolucionDeposito).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar devoluciones: {str(e)}")


# ---------------------------------------------------------
# Obtener devoluciones por contrato
# ---------------------------------------------------------
@router.get("/contrato/{id_contrato}", response_model=list[schemas.DevolucionDepositoResponse])
def devoluciones_por_contrato(id_contrato: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.DevolucionDeposito)
                .filter(models.DevolucionDeposito.contrato_id == id_contrato)
                .order_by(models.DevolucionDeposito.fecha_devolucion.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar devoluciones por contrato: {str(e)}")


# ---------------------------------------------------------
# Obtener devoluciones por inquilino
# ---------------------------------------------------------
@router.get("/inquilino/{cedula}", response_model=list[schemas.DevolucionDepositoResponse])
def devoluciones_por_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.DevolucionDeposito)
                .filter(models.DevolucionDeposito.inquilino_cedula == cedula)
                .order_by(models.DevolucionDeposito.fecha_devolucion.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar devoluciones por inquilino: {str(e)}")


# ---------------------------------------------------------
# Obtener una devolución específica (por contrato e inquilino)
# ---------------------------------------------------------
@router.get("/detalle/{id_contrato}/{cedula}", response_model=list[schemas.DevolucionDepositoResponse])
def detalle_devolucion(id_contrato: int, cedula: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.DevolucionDeposito)
                .filter(
                    models.DevolucionDeposito.contrato_id == id_contrato,
                    models.DevolucionDeposito.inquilino_cedula == cedula
                )
                .order_by(models.DevolucionDeposito.fecha_devolucion.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle de devolución: {str(e)}")


# ---------------------------------------------------------
# Actualizar devolución
# ---------------------------------------------------------
@router.put("/{id_contrato}/{cedula}/{fecha}", response_model=schemas.DevolucionDepositoResponse)
def actualizar_devolucion(id_contrato: int, cedula: str, fecha: str, datos: schemas.DevolucionDepositoCreate):
    try:
        with SessionLocal() as db:
            devolucion = (
                db.query(models.DevolucionDeposito)
                .filter(
                    models.DevolucionDeposito.contrato_id == id_contrato,
                    models.DevolucionDeposito.inquilino_cedula == cedula,
                    models.DevolucionDeposito.fecha_devolucion == fecha
                )
                .first()
            )
            if not devolucion:
                raise HTTPException(status_code=404, detail="Devolución no encontrada")

            for campo, valor in datos.dict(exclude_unset=True).items():
                setattr(devolucion, campo, valor)

            db.commit()
            db.refresh(devolucion)
            return devolucion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar devolución: {str(e)}")


# ---------------------------------------------------------
# Eliminar devolución
# ---------------------------------------------------------
@router.delete("/{id_contrato}/{cedula}/{fecha}")
def eliminar_devolucion(id_contrato: int, cedula: str, fecha: str):
    try:
        with SessionLocal() as db:
            devolucion = (
                db.query(models.DevolucionDeposito)
                .filter(
                    models.DevolucionDeposito.contrato_id == id_contrato,
                    models.DevolucionDeposito.inquilino_cedula == cedula,
                    models.DevolucionDeposito.fecha_devolucion == fecha
                )
                .first()
            )
            if not devolucion:
                raise HTTPException(status_code=404, detail="Devolución no encontrada")

            db.delete(devolucion)
            db.commit()
            return {"mensaje": "Devolución eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar devolución: {str(e)}")


# ---------------------------------------------------------
# Adjuntar foto de comprobante de devolución
# ---------------------------------------------------------
@router.post("/{id_contrato}/{cedula}/{fecha}/foto", response_model=schemas.FotoResponse)
def agregar_foto_devolucion(id_contrato: int, cedula: str, fecha: str, foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            devolucion = (
                db.query(models.DevolucionDeposito)
                .filter(
                    models.DevolucionDeposito.contrato_id == id_contrato,
                    models.DevolucionDeposito.inquilino_cedula == cedula,
                    models.DevolucionDeposito.fecha_devolucion == fecha
                )
                .first()
            )
            if not devolucion:
                raise HTTPException(status_code=404, detail="Devolución no encontrada")

            nueva_foto = models.Foto(**foto.dict())
            db.add(nueva_foto)
            db.commit()
            db.refresh(nueva_foto)

            devolucion.id_foto = nueva_foto.id
            db.commit()
            db.refresh(devolucion)

            return nueva_foto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar foto a devolución: {str(e)}")
