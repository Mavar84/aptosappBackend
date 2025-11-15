from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from security import get_current_user
import models, schemas

router = APIRouter(
    prefix="/apartamentos",
    tags=["Apartamentos"],
    dependencies=[Depends(get_current_user)]  # 🔒 Todos los endpoints requieren login
)

# ---------------------------------------------------------
# Crear apartamento
# ---------------------------------------------------------
@router.post("/", response_model=schemas.ApartamentoResponse)
def crear_apartamento(apto: schemas.ApartamentoCreate):
    try:
        with SessionLocal() as db:
            nuevo = models.Apartamento(**apto.dict())
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear apartamento: {str(e)}")


# ---------------------------------------------------------
# Listar todos los apartamentos
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.ApartamentoResponse])
def listar_apartamentos():
    try:
        with SessionLocal() as db:
            return db.query(models.Apartamento).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar apartamentos: {str(e)}")


# ---------------------------------------------------------
# Obtener apartamento por ID
# ---------------------------------------------------------
@router.get("/{id}", response_model=schemas.ApartamentoResponse)
def obtener_apartamento(id: int):
    try:
        with SessionLocal() as db:
            apto = db.query(models.Apartamento).filter(models.Apartamento.id == id).first()
            if not apto:
                raise HTTPException(status_code=404, detail="Apartamento no encontrado")
            return apto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener apartamento: {str(e)}")


# ---------------------------------------------------------
# Actualizar apartamento
# ---------------------------------------------------------
@router.put("/{id}", response_model=schemas.ApartamentoResponse)
def actualizar_apartamento(id: int, datos: schemas.ApartamentoCreate):
    try:
        with SessionLocal() as db:
            apto = db.query(models.Apartamento).filter(models.Apartamento.id == id).first()
            if not apto:
                raise HTTPException(status_code=404, detail="Apartamento no encontrado")

            for campo, valor in datos.dict(exclude_unset=True).items():
                setattr(apto, campo, valor)

            db.commit()
            db.refresh(apto)
            return apto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar apartamento: {str(e)}")


# ---------------------------------------------------------
# Eliminar apartamento
# ---------------------------------------------------------
@router.delete("/{id}")
def eliminar_apartamento(id: int):
    try:
        with SessionLocal() as db:
            apto = db.query(models.Apartamento).filter(models.Apartamento.id == id).first()
            if not apto:
                raise HTTPException(status_code=404, detail="Apartamento no encontrado")
            db.delete(apto)
            db.commit()
            return {"mensaje": "Apartamento eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar apartamento: {str(e)}")


# ---------------------------------------------------------
# Búsqueda por nombre o dirección
# ---------------------------------------------------------
@router.get("/buscar/{texto}", response_model=list[schemas.ApartamentoResponse])
def buscar_apartamentos(texto: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.Apartamento)
                .filter(
                    (models.Apartamento.nombre.ilike(f"%{texto}%")) |
                    (models.Apartamento.direccion_fisica.ilike(f"%{texto}%"))
                )
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar apartamentos: {str(e)}")
