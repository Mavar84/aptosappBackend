from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, condecimal
from models import TipoPagoEnum


# ---------------------------------------------------------
# FOTO
# ---------------------------------------------------------

class FotoBase(BaseModel):
    contexto: Optional[str] = None


class FotoCreate(FotoBase):
    base64_parte1: Optional[str] = None
    base64_parte2: Optional[str] = None


class FotoResponse(FotoBase):
    id: int
    base64_parte1: Optional[str]
    base64_parte2: Optional[str]

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# APARTAMENTO
# ---------------------------------------------------------

class ApartamentoBase(BaseModel):
    nombre: Optional[str]
    tamanno_m2: Optional[condecimal(max_digits=10, decimal_places=3)]
    ejex: Optional[condecimal(max_digits=10, decimal_places=3)]
    ejey: Optional[condecimal(max_digits=10, decimal_places=3)]
    num_piso: Optional[int]
    num_cuartos: Optional[int]
    num_bannos: Optional[int]
    num_pilas: Optional[int]
    num_salas: Optional[int]
    num_cocina: Optional[int]
    num_comedor: Optional[int]
    color_interno: Optional[str]
    color_externo: Optional[str]
    num_ventanas: Optional[int]
    tiene_ducha: Optional[bool]
    num_220: Optional[int]
    num_closet: Optional[int]
    num_mueble_cocina: Optional[int]
    direccion_fisica: Optional[str]


class ApartamentoCreate(ApartamentoBase):
    pass


class ApartamentoResponse(ApartamentoBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# INQUILINO
# ---------------------------------------------------------

class InquilinoBase(BaseModel):
    cedula: str
    nombre: Optional[str]
    p_apellido: Optional[str]
    s_apellido: Optional[str]
    nacionalidad: Optional[str]
    fecha_nac: Optional[datetime]
    celular: Optional[str]
    correo: Optional[EmailStr]
    genero: Optional[int]
    profesion: Optional[str]


class InquilinoCreate(InquilinoBase):
    pass


class InquilinoResponse(InquilinoBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# CONTRATO
# ---------------------------------------------------------

class ContratoBase(BaseModel):
    id_apartamento: Optional[int]
    fecha_formalizacion: Optional[datetime]
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    monto_mensual_inicial: Optional[condecimal(max_digits=10, decimal_places=3)]
    monto_deposito_inicial: Optional[condecimal(max_digits=10, decimal_places=3)]
    recibos_incluidos: Optional[bool]
    incluye_cable: Optional[bool]
    incluye_internet: Optional[bool]
    incluye_parqueo: Optional[bool]
    cantidad_personas: Optional[int]
    cantidad_mascotas: Optional[int]
    dia_pago_mes: Optional[int]
    fecha_maxima_pago_deposito: Optional[datetime]
    dia_pago_agua: Optional[int]
    dia_pago_luz: Optional[int]
    estado: Optional[int]
    otros_detalles: Optional[str]


class ContratoCreate(ContratoBase):
    pass


class ContratoResponse(ContratoBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# CONTRATO-INQUILINO (relación)
# ---------------------------------------------------------

class ContratoInquilinoBase(BaseModel):
    id_contrato: int
    cedula_inquilino: str
    prioridad: Optional[int]


class ContratoInquilinoCreate(ContratoInquilinoBase):
    pass


class ContratoInquilinoResponse(ContratoInquilinoBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# MONTOS ACTUALES
# ---------------------------------------------------------

class MontoActualBase(BaseModel):
    contrato_id: int
    fecha_ult_act: Optional[datetime] = None
    monto_mensualidad: Optional[condecimal(max_digits=10, decimal_places=3)]
    estado: Optional[int]


class MontoActualResponse(MontoActualBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# PAGOS MENSUALES
# ---------------------------------------------------------

class PagoMensualBase(BaseModel):
    fecha_pago: Optional[datetime]
    monto_pagado: Optional[condecimal(max_digits=10, decimal_places=3)]
    es_pago_completo: Optional[bool]
    monto_adeudado_de_este_pago: Optional[condecimal(max_digits=10, decimal_places=3)]
    tipo: Optional[TipoPagoEnum]
    monto_esperado: Optional[condecimal(max_digits=10, decimal_places=3)]
    estado: Optional[int]
    contrato_id: int
    inquilino_cedula: str
    fecha_vence: Optional[datetime]
    mes: Optional[int]
    anno: Optional[int]
    detalle: Optional[str]


class PagoMensualCreate(PagoMensualBase):
    pass


class PagoMensualResponse(PagoMensualBase):
    id: int

    class Config:
        orm_mode = True






# ---------------------------------------------------------
# INQUILINOS - FOTOS
# ---------------------------------------------------------

class InquilinoFotoBase(BaseModel):
    cedula_inquilino: str
    id_foto: int
    contexto: Optional[str]


class PnquilinoFotoResponse(InquilinoFotoBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# PAGOS - FOTOS
# ---------------------------------------------------------

class PagoFotoBase(BaseModel):
    id_pago: int
    id_foto: int
    detalle: Optional[str]


class PagoFotoResponse(PagoFotoBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# DEVOLUCIÓN DE DEPÓSITO
# ---------------------------------------------------------

class DevolucionDepositoBase(BaseModel):
    contrato_id: int
    inquilino_cedula: str
    fecha_devolucion: Optional[datetime]
    rebajos_aplicados: Optional[str]
    monto_original: Optional[condecimal(max_digits=10, decimal_places=3)]
    monto_devuelto: Optional[condecimal(max_digits=10, decimal_places=3)]
    otros_detalles: Optional[str]
    id_foto: Optional[int]


class DevolucionDepositoCreate(DevolucionDepositoBase):
    pass


class DevolucionDepositoResponse(DevolucionDepositoBase):
    class Config:
        orm_mode = True


# ---------------------------------------------------------
# RESPUESTAS ANIDADAS (para listar con detalle)
# ---------------------------------------------------------

class ContratoDetalleResponse(ContratoResponse):
    inquilinos: Optional[List[ContratoInquilinoResponse]] = None
    montos: Optional[List[MontoActualResponse]] = None
    devoluciones: Optional[List[DevolucionDepositoResponse]] = None

from typing import Literal
from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    correo: EmailStr
    nombre: str | None = None
    p_apellido: str | None = None
    s_apellido: str | None = None
    celular: str | None = None
    rol: Literal["admin", "gestor", "usuario"] = "usuario"
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    clave: str = Field(min_length=8, max_length=128)

class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    p_apellido: str | None = None
    s_apellido: str | None = None
    celular: str | None = None
    rol: Literal["admin", "gestor", "usuario"] | None = None
    activo: bool | None = None
    clave: str | None = Field(default=None, min_length=8, max_length=128)

class UsuarioResponse(UsuarioBase):
    id: int
    class Config:
        from_attributes = True

# Esquemas de autenticación
class LoginRequest(BaseModel):
    correo: EmailStr
    clave: str

class TokenData(BaseModel):
    sub: str
    rol: str
