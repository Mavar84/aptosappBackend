from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from database import SessionLocal
import models, schemas
from security import get_current_user

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos Mensuales"],
    dependencies=[Depends(get_current_user)]  # 🔒 todos los endpoints requieren login
)

# ---------------------------------------------------------
# Registrar nuevo pago mensual
# ---------------------------------------------------------
@router.post("/", response_model=schemas.PagoMensualResponse)
def registrar_pago(pago: schemas.PagoMensualCreate):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == pago.contrato_id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no existe")

            inquilino = db.query(models.Inquilino).filter(models.Inquilino.cedula == pago.inquilino_cedula).first()
            if not inquilino:
                raise HTTPException(status_code=404, detail="Inquilino no existe")

            nuevo_pago = models.PagoMensual(**pago.dict())
            db.add(nuevo_pago)
            db.commit()
            db.refresh(nuevo_pago)
            return nuevo_pago
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar pago: {str(e)}")


# ---------------------------------------------------------
# Listar todos los pagos
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.PagoMensualResponse])
def listar_pagos():
    try:
        with SessionLocal() as db:
            return db.query(models.PagoMensual).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar pagos: {str(e)}")


# ---------------------------------------------------------
# Obtener pago por ID
# ---------------------------------------------------------
@router.get("/{id}", response_model=schemas.PagoMensualResponse)
def obtener_pago(id: int):
    try:
        with SessionLocal() as db:
            pago = db.query(models.PagoMensual).filter(models.PagoMensual.id == id).first()
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no encontrado")
            return pago
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pago: {str(e)}")


# ---------------------------------------------------------
# Actualizar pago
# ---------------------------------------------------------
@router.put("/{id}", response_model=schemas.PagoMensualResponse)
def actualizar_pago(id: int, datos: schemas.PagoMensualCreate):
    try:
        with SessionLocal() as db:
            pago = db.query(models.PagoMensual).filter(models.PagoMensual.id == id).first()
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no encontrado")

            for campo, valor in datos.dict(exclude_unset=True).items():
                setattr(pago, campo, valor)

            db.commit()
            db.refresh(pago)
            return pago
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar pago: {str(e)}")


# ---------------------------------------------------------
# Eliminar pago
# ---------------------------------------------------------
@router.delete("/{id}")
def eliminar_pago(id: int):
    try:
        with SessionLocal() as db:
            pago = db.query(models.PagoMensual).filter(models.PagoMensual.id == id).first()
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no encontrado")
            db.delete(pago)
            db.commit()
            return {"mensaje": "Pago eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar pago: {str(e)}")


# ---------------------------------------------------------
# Listar pagos por contrato
# ---------------------------------------------------------
@router.get("/contrato/{id_contrato}", response_model=list[schemas.PagoMensualResponse])
def listar_pagos_por_contrato(id_contrato: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.PagoMensual)
                .filter(models.PagoMensual.contrato_id == id_contrato)
                .order_by(models.PagoMensual.fecha_pago.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar pagos por contrato: {str(e)}")


# ---------------------------------------------------------
# Listar pagos por inquilino
# ---------------------------------------------------------
@router.get("/inquilino/{cedula}", response_model=list[schemas.PagoMensualResponse])
def listar_pagos_por_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.PagoMensual)
                .filter(models.PagoMensual.inquilino_cedula == cedula)
                .order_by(models.PagoMensual.fecha_pago.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar pagos por inquilino: {str(e)}")


# ---------------------------------------------------------
# Buscar pagos por tipo (mensualidad, depósito, agua, luz, parqueo)
# ---------------------------------------------------------
@router.get("/tipo/{tipo}", response_model=list[schemas.PagoMensualResponse])
def listar_pagos_por_tipo(tipo: str):
    try:
        with SessionLocal() as db:
            try:
                tipo_enum = getattr(models.TipoPagoEnum, tipo)
            except AttributeError:
                raise HTTPException(status_code=400, detail="Tipo de pago no válido")

            return db.query(models.PagoMensual).filter(models.PagoMensual.tipo == tipo_enum).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar pagos por tipo: {str(e)}")


# ---------------------------------------------------------
# Registrar foto de un pago
# ---------------------------------------------------------
@router.post("/{id_pago}/foto", response_model=schemas.PagoFotoResponse)
def agregar_foto_a_pago(id_pago: int, foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            pago = db.query(models.PagoMensual).filter(models.PagoMensual.id == id_pago).first()
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no encontrado")

            nueva_foto = models.Foto(**foto.dict())
            db.add(nueva_foto)
            db.commit()
            db.refresh(nueva_foto)

            relacion = models.PagoFoto(id_pago=id_pago, id_foto=nueva_foto.id)
            db.add(relacion)
            db.commit()
            db.refresh(relacion)
            return relacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar foto al pago: {str(e)}")


# ---------------------------------------------------------
# Obtener todas las fotos de un pago
# ---------------------------------------------------------
@router.get("/{id_pago}/fotos", response_model=list[schemas.FotoResponse])
def obtener_fotos_pago(id_pago: int):
    try:
        with SessionLocal() as db:
            fotos = (
                db.query(models.Foto)
                .join(models.PagoFoto)
                .filter(models.PagoFoto.id_pago == id_pago)
                .all()
            )
            return fotos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener fotos del pago: {str(e)}")
