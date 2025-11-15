from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
import models, schemas
from security import get_current_user

router = APIRouter(
    prefix="/fotos",
    tags=["Fotos"],
    dependencies=[Depends(get_current_user)]  # 🔒 Todos los endpoints requieren login
)

# ---------------------------------------------------------
# CRUD GENERAL DE FOTOS
# ---------------------------------------------------------

@router.post("/", response_model=schemas.FotoResponse)
def crear_foto(foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            nueva = models.Foto(**foto.dict())
            db.add(nueva)
            db.commit()
            db.refresh(nueva)
            return nueva
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear foto: {str(e)}")


@router.get("/", response_model=list[schemas.FotoResponse])
def listar_fotos():
    try:
        with SessionLocal() as db:
            return db.query(models.Foto).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(e)}")


@router.get("/{id}", response_model=schemas.FotoResponse)
def obtener_foto(id: int):
    try:
        with SessionLocal() as db:
            foto = db.query(models.Foto).filter(models.Foto.id == id).first()
            if not foto:
                raise HTTPException(status_code=404, detail="Foto no encontrada")
            return foto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener foto: {str(e)}")


@router.delete("/{id}")
def eliminar_foto(id: int):
    try:
        with SessionLocal() as db:
            foto = db.query(models.Foto).filter(models.Foto.id == id).first()
            if not foto:
                raise HTTPException(status_code=404, detail="Foto no encontrada")
            db.delete(foto)
            db.commit()
            return {"mensaje": "Foto eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar foto: {str(e)}")


# ---------------------------------------------------------
# BÚSQUEDAS POR CONTEXTO
# ---------------------------------------------------------

@router.get("/buscar/{contexto}", response_model=list[schemas.FotoResponse])
def buscar_fotos_por_contexto(contexto: str):
    try:
        with SessionLocal() as db:
            return db.query(models.Foto).filter(models.Foto.contexto.ilike(f"%{contexto}%")).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar fotos: {str(e)}")


# ---------------------------------------------------------
# RELACIONES: APARTAMENTO - FOTOS
# ---------------------------------------------------------

@router.post("/apartamento/{id_apto}")
def agregar_fotos_apartamento(id_apto: int, fotos: list[schemas.FotoCreate]):
    try:
        with SessionLocal() as db:
            for f in fotos:
                nueva_foto = models.Foto(
                    contexto=f.contexto,
                    base64_parte1=f.base64_parte1,
                    base64_parte2=f.base64_parte2,
                )
                db.add(nueva_foto)
                db.flush()
                enlace = models.ApartamentoFoto(id_apto=id_apto, id_foto=nueva_foto.id)
                db.add(enlace)
            db.commit()
            return {"mensaje": "Todas las fotos guardadas correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar fotos: {str(e)}")


@router.get("/apartamento/{id_apto}", response_model=list[schemas.FotoResponse])
def listar_fotos_apartamento(id_apto: int):
    try:
        with SessionLocal() as db:
            fotos = (
                db.query(models.Foto)
                .join(models.ApartamentoFoto)
                .filter(models.ApartamentoFoto.id_apto == id_apto)
                .all()
            )
            return fotos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(e)}")


@router.delete("/apartamento/{id_apto}/{id_foto}")
def eliminar_foto_apartamento(id_apto: int, id_foto: int):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.ApartamentoFoto)
                .filter(models.ApartamentoFoto.id_apto == id_apto,
                        models.ApartamentoFoto.id_foto == id_foto)
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación no encontrada")
            db.delete(relacion)
            db.commit()
            return {"mensaje": "Foto desvinculada del apartamento"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar foto: {str(e)}")


# ---------------------------------------------------------
# RELACIONES: CONTRATO - FOTOS
# ---------------------------------------------------------

@router.post("/contrato/{id_contrato}", response_model=schemas.FotoResponse)
def agregar_foto_contrato(id_contrato: int, foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == id_contrato).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no existe")

            nueva_foto = models.Foto(**foto.dict())
            db.add(nueva_foto)
            db.commit()
            db.refresh(nueva_foto)

            relacion = models.ContratoFoto(id_contrato=id_contrato, id_foto=nueva_foto.id)
            db.add(relacion)
            db.commit()
            db.refresh(nueva_foto)
            return nueva_foto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar foto: {str(e)}")


@router.get("/contrato/{id_contrato}", response_model=list[schemas.FotoResponse])
def listar_fotos_contrato(id_contrato: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.Foto)
                .join(models.ContratoFoto)
                .filter(models.ContratoFoto.id_contrato == id_contrato)
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(e)}")


@router.delete("/contrato/{id_contrato}/{id_foto}")
def eliminar_foto_contrato(id_contrato: int, id_foto: int):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.ContratoFoto)
                .filter(models.ContratoFoto.id_contrato == id_contrato,
                        models.ContratoFoto.id_foto == id_foto)
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación no encontrada")
            db.delete(relacion)
            db.commit()
            return {"mensaje": "Foto desvinculada del contrato"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar foto: {str(e)}")


# ---------------------------------------------------------
# RELACIONES: INQUILINO - FOTOS
# ---------------------------------------------------------

@router.post("/inquilino/{cedula}", response_model=schemas.FotoResponse)
def agregar_foto_inquilino(cedula: str, foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            inq = db.query(models.Inquilino).filter(models.Inquilino.cedula == cedula).first()
            if not inq:
                raise HTTPException(status_code=404, detail="Inquilino no existe")

            nueva_foto = models.Foto(**foto.dict())
            db.add(nueva_foto)
            db.commit()
            db.refresh(nueva_foto)

            relacion = models.InquilinoFoto(cedula_inquilino=cedula, id_foto=nueva_foto.id)
            db.add(relacion)
            db.commit()
            db.refresh(nueva_foto)
            return nueva_foto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar foto: {str(e)}")


@router.get("/inquilino/{cedula}", response_model=list[schemas.FotoResponse])
def listar_fotos_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.Foto)
                .join(models.InquilinoFoto)
                .filter(models.InquilinoFoto.cedula_inquilino == cedula)
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(e)}")


@router.delete("/inquilino/{cedula}/{id_foto}")
def eliminar_foto_inquilino(cedula: str, id_foto: int):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.InquilinoFoto)
                .filter(models.InquilinoFoto.cedula_inquilino == cedula,
                        models.InquilinoFoto.id_foto == id_foto)
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación no encontrada")
            db.delete(relacion)
            db.commit()
            return {"mensaje": "Foto desvinculada del inquilino"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar foto: {str(e)}")


# ---------------------------------------------------------
# RELACIONES: PAGO - FOTOS
# ---------------------------------------------------------

@router.post("/pago/{id_pago}", response_model=schemas.FotoResponse)
def agregar_foto_pago(id_pago: int, foto: schemas.FotoCreate):
    try:
        with SessionLocal() as db:
            pago = db.query(models.PagoMensual).filter(models.PagoMensual.id == id_pago).first()
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no existe")

            nueva_foto = models.Foto(**foto.dict())
            db.add(nueva_foto)
            db.commit()
            db.refresh(nueva_foto)

            relacion = models.PagoFoto(id_pago=id_pago, id_foto=nueva_foto.id)
            db.add(relacion)
            db.commit()
            db.refresh(nueva_foto)
            return nueva_foto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar foto: {str(e)}")


@router.get("/pago/{id_pago}", response_model=list[schemas.FotoResponse])
def listar_fotos_pago(id_pago: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.Foto)
                .join(models.PagoFoto)
                .filter(models.PagoFoto.id_pago == id_pago)
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(e)}")


@router.delete("/pago/{id_pago}/{id_foto}")
def eliminar_foto_pago(id_pago: int, id_foto: int):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.PagoFoto)
                .filter(models.PagoFoto.id_pago == id_pago,
                        models.PagoFoto.id_foto == id_foto)
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación no encontrada")
            db.delete(relacion)
            db.commit()
            return {"mensaje": "Foto desvinculada del pago"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar foto: {str(e)}")
