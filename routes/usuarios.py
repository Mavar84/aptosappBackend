from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
from database import SessionLocal
import models, schemas
from security import make_password_hash, require_roles

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ---------------------------------------------------------
# Registro público (nuevo usuario con rol "usuario")
# ---------------------------------------------------------
@router.post("/registro", response_model=schemas.UsuarioResponse, status_code=201)
def registro_publico(data: schemas.UsuarioCreate):
    try:
        with SessionLocal() as db:
            existente = db.query(models.Usuario).filter(models.Usuario.correo == data.correo).first()
            if existente:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")

            salt = uuid4().hex
            hashed = make_password_hash(data.clave, salt)

            nuevo = models.Usuario(
                correo=data.correo,
                clave_hash=hashed,
                salt=salt,
                nombre=data.nombre,
                p_apellido=data.p_apellido,
                s_apellido=data.s_apellido,
                celular=data.celular,
                rol=models.RolEnum("usuario"),
                activo=True
            )

            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)

            # Convertir Enum a string antes de devolver
            nuevo.rol = nuevo.rol.value
            return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")


# ---------------------------------------------------------
# Crear usuario (solo admin)
# ---------------------------------------------------------
@router.post("/", response_model=schemas.UsuarioResponse, status_code=201, dependencies=[Depends(require_roles("admin"))])
def crear_usuario(data: schemas.UsuarioCreate):
    try:
        with SessionLocal() as db:
            existente = db.query(models.Usuario).filter(models.Usuario.correo == data.correo).first()
            if existente:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")

            salt = uuid4().hex
            hashed = make_password_hash(data.clave, salt)

            nuevo = models.Usuario(
                correo=data.correo,
                clave_hash=hashed,
                salt=salt,
                nombre=data.nombre,
                p_apellido=data.p_apellido,
                s_apellido=data.s_apellido,
                celular=data.celular,
                rol=models.RolEnum(data.rol),
                activo=data.activo
            )

            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            nuevo.rol = nuevo.rol.value
            return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")


# ---------------------------------------------------------
# Listar todos los usuarios (solo admin)
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.UsuarioResponse], dependencies=[Depends(require_roles("admin"))])
def listar_usuarios():
    try:
        with SessionLocal() as db:
            usuarios = db.query(models.Usuario).all()
            for u in usuarios:
                u.rol = u.rol.value
            return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar usuarios: {str(e)}")


# ---------------------------------------------------------
# Obtener usuario por ID (solo admin)
# ---------------------------------------------------------
@router.get("/{usuario_id}", response_model=schemas.UsuarioResponse, dependencies=[Depends(require_roles("admin"))])
def obtener_usuario(usuario_id: int):
    try:
        with SessionLocal() as db:
            user = db.query(models.Usuario).get(usuario_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            user.rol = user.rol.value
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")


# ---------------------------------------------------------
# Actualizar usuario (solo admin)
# ---------------------------------------------------------
@router.put("/{usuario_id}", response_model=schemas.UsuarioResponse, dependencies=[Depends(require_roles("admin"))])
def actualizar_usuario(usuario_id: int, data: schemas.UsuarioUpdate):
    try:
        with SessionLocal() as db:
            user = db.query(models.Usuario).get(usuario_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            if data.nombre is not None:
                user.nombre = data.nombre
            if data.p_apellido is not None:
                user.p_apellido = data.p_apellido
            if data.s_apellido is not None:
                user.s_apellido = data.s_apellido
            if data.celular is not None:
                user.celular = data.celular
            if data.rol is not None:
                user.rol = models.RolEnum(data.rol)
            if data.activo is not None:
                user.activo = data.activo
            if data.clave:
                salt = uuid4().hex
                user.salt = salt
                user.clave_hash = make_password_hash(data.clave, salt)

            db.commit()
            db.refresh(user)
            user.rol = user.rol.value
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")


# ---------------------------------------------------------
# Eliminar usuario (solo admin)
# ---------------------------------------------------------
@router.delete("/{usuario_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def eliminar_usuario(usuario_id: int):
    try:
        with SessionLocal() as db:
            user = db.query(models.Usuario).get(usuario_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            db.delete(user)
            db.commit()
            return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")
