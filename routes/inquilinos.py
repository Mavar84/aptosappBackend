from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
import models, schemas
from security import get_current_user

router = APIRouter(
    prefix="/inquilinos",
    tags=["Inquilinos"],
    dependencies=[Depends(get_current_user)]  # 🔒 todos los endpoints requieren login
)

# ---------------------------------------------------------
# Crear inquilino
# ---------------------------------------------------------
@router.post("/", response_model=schemas.InquilinoResponse)
def crear_inquilino(inquilino: schemas.InquilinoCreate):
    try:
        with SessionLocal() as db:
            existente = db.query(models.Inquilino).filter(models.Inquilino.cedula == inquilino.cedula).first()
            if existente:
                raise HTTPException(status_code=400, detail="Ya existe un inquilino con esa cédula")

            nuevo = models.Inquilino(**inquilino.dict())
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear inquilino: {str(e)}")


# ---------------------------------------------------------
# Listar todos los inquilinos
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.InquilinoResponse])
def listar_inquilinos():
    try:
        with SessionLocal() as db:
            return db.query(models.Inquilino).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar inquilinos: {str(e)}")


# ---------------------------------------------------------
# Obtener inquilino por cédula
# ---------------------------------------------------------
@router.get("/{cedula}", response_model=schemas.InquilinoResponse)
def obtener_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            inq = db.query(models.Inquilino).filter(models.Inquilino.cedula == cedula).first()
            if not inq:
                raise HTTPException(status_code=404, detail="Inquilino no encontrado")
            return inq
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener inquilino: {str(e)}")


# ---------------------------------------------------------
# Actualizar inquilino
# ---------------------------------------------------------
@router.put("/{cedula}", response_model=schemas.InquilinoResponse)
def actualizar_inquilino(cedula: str, datos: schemas.InquilinoCreate):
    try:
        with SessionLocal() as db:
            inq = db.query(models.Inquilino).filter(models.Inquilino.cedula == cedula).first()
            if not inq:
                raise HTTPException(status_code=404, detail="Inquilino no encontrado")

            for campo, valor in datos.dict(exclude_unset=True).items():
                setattr(inq, campo, valor)

            db.commit()
            db.refresh(inq)
            return inq
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar inquilino: {str(e)}")


# ---------------------------------------------------------
# Eliminar inquilino
# ---------------------------------------------------------
@router.delete("/{cedula}")
def eliminar_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            inq = db.query(models.Inquilino).filter(models.Inquilino.cedula == cedula).first()
            if not inq:
                raise HTTPException(status_code=404, detail="Inquilino no encontrado")

            db.delete(inq)
            db.commit()
            return {"mensaje": "Inquilino eliminado correctamente"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=f"Error al eliminar inquilino: {str(e)}")


# ---------------------------------------------------------
# Buscar por nombre, apellido o correo
# ---------------------------------------------------------
@router.get("/buscar/{texto}", response_model=list[schemas.InquilinoResponse])
def buscar_inquilinos(texto: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.Inquilino)
                .filter(
                    (models.Inquilino.nombre.ilike(f"%{texto}%")) |
                    (models.Inquilino.p_apellido.ilike(f"%{texto}%")) |
                    (models.Inquilino.s_apellido.ilike(f"%{texto}%")) |
                    (models.Inquilino.correo.ilike(f"%{texto}%"))
                )
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar inquilinos: {str(e)}")
