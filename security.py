import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from sqlalchemy.orm import Session

from database import get_db
import models

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

import hashlib


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def make_password_hash(plain_password: str, salt: str) -> str:
    # Mezclamos password y salt en una forma corta antes de pasar a bcrypt
    combined = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return pwd_context.hash(combined)

def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    combined = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return pwd_context.verify(combined, hashed_password)


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_correo(db: Session, correo: str) -> Optional[models.Usuario]:
    return db.query(models.Usuario).filter(models.Usuario.correo == correo).first()

# ======================================================
# Función para obtener el usuario actual (cookie o header)
# ======================================================
def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
    access_token: str = Cookie(None)
):
    token = None

    # 1️⃣ Si viene el token en header Authorization: Bearer <token>
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    # 2️⃣ Si viene en cookie (caso navegador)
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(status_code=401, detail="No se encontró token de autenticación")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not user or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    return user

def require_roles(*roles_permitidos: str):
    def checker(user: models.Usuario = Depends(get_current_user)):
        if user.rol.value not in roles_permitidos:
            raise HTTPException(status_code=403, detail="No tiene permisos")
        return user
    return checker
