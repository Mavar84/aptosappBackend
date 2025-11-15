from fastapi import APIRouter, Depends, HTTPException, Response, status
from datetime import timedelta
from database import SessionLocal
import models, schemas
from security import get_user_by_correo, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

COOKIE_NAME = "access_token"

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login")
def login(payload: schemas.LoginRequest, response: Response):
    try:
        with SessionLocal() as db:
            user = get_user_by_correo(db, payload.correo)
            if not user or not user.activo:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            if not verify_password(payload.clave, user.salt, user.clave_hash):
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            token = create_access_token({"sub": user.correo, "rol": user.rol.value})

            # Guarda cookie para navegadores
            response.set_cookie(
                key=COOKIE_NAME,
                value=token,
                httponly=True,
                samesite="lax",  # Cambiar a 'none' si frontend está en dominio diferente (https)
                secure=False,    # Cambiar a True en producción con HTTPS
                max_age=60 * 60,  # 1 hora
                path="/"
            )

            return {
                "mensaje": "Login correcto",
                "access_token": token,
                "token_type": "bearer",
                "usuario": {
                    "id": user.id,
                    "correo": user.correo,
                    "nombre": user.nombre,
                    "rol": user.rol.value,
                    "activo": user.activo
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar sesión: {str(e)}")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@router.post("/logout")
def logout(response: Response):
    try:
        response.delete_cookie(key=COOKIE_NAME, path="/")
        return {"mensaje": "Logout correcto"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cerrar sesión: {str(e)}")


# ---------------------------------------------------------
# QUIÉN SOY
# ---------------------------------------------------------
@router.get("/me", response_model=schemas.UsuarioResponse)
def quien_soy(user: models.Usuario = Depends(get_current_user)):
    try:
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")
