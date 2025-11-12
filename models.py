from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, Text, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class TipoPagoEnum(enum.Enum):
    mensualidad = 1
    deposito = 2
    agua = 3
    luz = 4
    parqueo = 5


# ---------------------------------------------------------
# MODELOS BASE
# ---------------------------------------------------------

class Foto(Base):
    __tablename__ = "fotos"

    id = Column(Integer, primary_key=True, index=True)
    base64_parte1 = Column(Text, nullable=True)
    base64_parte2 = Column(Text, nullable=True)
    contexto = Column(String(400), nullable=True)

    apartamento_fotos = relationship("ApartamentoFoto", back_populates="foto")
    contrato_fotos = relationship("ContratoFoto", back_populates="foto")
    inquilino_fotos = relationship("InquilinoFoto", back_populates="foto")
    pagos_fotos = relationship("PagoFoto", back_populates="foto")
    devoluciones = relationship("DevolucionDeposito", back_populates="foto")


class Apartamento(Base):
    __tablename__ = "apartamento"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200))
    tamanno_m2 = Column(Numeric(10, 3))
    ejex = Column(Numeric(10, 3))
    ejey = Column(Numeric(10, 3))
    num_piso = Column(Integer)
    num_cuartos = Column(Integer)
    num_bannos = Column(Integer)
    num_pilas = Column(Integer)
    num_salas = Column(Integer)
    num_cocina = Column(Integer)
    num_comedor = Column(Integer)
    color_interno = Column(String(100))
    color_externo = Column(String(100))
    num_ventanas = Column(Integer)
    tiene_ducha = Column(Boolean)
    num_220 = Column(Integer)
    num_closet = Column(Integer)
    num_mueble_cocina = Column(Integer)
    direccion_fisica = Column(String(500))

    contratos = relationship("Contrato", back_populates="apartamento")
    fotos = relationship("ApartamentoFoto", back_populates="apartamento")


class Inquilino(Base):
    __tablename__ = "inquilino"

    cedula = Column(String(100), primary_key=True, index=True)
    nombre = Column(String(100))
    p_apellido = Column(String(100))
    s_apellido = Column(String(100))
    nacionalidad = Column(String(500))
    fecha_nac = Column(DateTime)
    celular = Column(String(50))
    correo = Column(String(100))
    genero = Column(Integer)
    profesion = Column(String(400))

    contratos = relationship("ContratoInquilino", back_populates="inquilino")
    fotos = relationship("InquilinoFoto", back_populates="inquilino")
    pagos = relationship("PagoMensual", back_populates="inquilino")
    devoluciones = relationship("DevolucionDeposito", back_populates="inquilino")


# ---------------------------------------------------------
# RELACIONES INTERMEDIAS (muchos a muchos)
# ---------------------------------------------------------

class ApartamentoFoto(Base):
    __tablename__ = "apartamento_fotos"

    id_apto = Column(Integer, ForeignKey("apartamento.id", ondelete="CASCADE"), primary_key=True)
    id_foto = Column(Integer, ForeignKey("fotos.id", ondelete="CASCADE"), primary_key=True)
    descripcion = Column(String(400))

    apartamento = relationship("Apartamento", back_populates="fotos")
    foto = relationship("Foto", back_populates="apartamento_fotos")


class Contrato(Base):
    __tablename__ = "contrato"

    id = Column(Integer, primary_key=True, index=True)
    id_apartamento = Column(Integer, ForeignKey("apartamento.id", ondelete="SET NULL"))
    fecha_formalizacion = Column(DateTime, default=datetime.utcnow)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    monto_mensual_inicial = Column(Numeric(10, 3))
    monto_deposito_inicial = Column(Numeric(10, 3))
    recibos_incluidos = Column(Boolean)
    incluye_cable = Column(Boolean)
    incluye_internet = Column(Boolean)
    incluye_parqueo = Column(Boolean)
    cantidad_personas = Column(Integer)
    cantidad_mascotas = Column(Integer)
    dia_pago_mes = Column(Integer)
    fecha_maxima_pago_deposito = Column(DateTime)
    dia_pago_agua = Column(Integer)
    dia_pago_luz = Column(Integer)
    estado = Column(Integer)
    otros_detalles = Column(String(500))

    apartamento = relationship("Apartamento", back_populates="contratos")
    inquilinos = relationship("ContratoInquilino", back_populates="contrato")
    fotos = relationship("ContratoFoto", back_populates="contrato")
    montos = relationship("MontoActual", back_populates="contrato")
    pagos = relationship("PagoMensual", back_populates="contrato")
    devoluciones = relationship("DevolucionDeposito", back_populates="contrato")


class ContratoInquilino(Base):
    __tablename__ = "contrato_inquilino"

    id_contrato = Column(Integer, ForeignKey("contrato.id", ondelete="CASCADE"), primary_key=True)
    cedula_inquilino = Column(String(100), ForeignKey("inquilino.cedula", ondelete="CASCADE"), primary_key=True)
    prioridad = Column(Integer)

    contrato = relationship("Contrato", back_populates="inquilinos")
    inquilino = relationship("Inquilino", back_populates="contratos")


class ContratoFoto(Base):
    __tablename__ = "contrato_foto"

    id_contrato = Column(Integer, ForeignKey("contrato.id", ondelete="CASCADE"), primary_key=True)
    id_foto = Column(Integer, ForeignKey("fotos.id", ondelete="CASCADE"), primary_key=True)
    detalle = Column(String(100))

    contrato = relationship("Contrato", back_populates="fotos")
    foto = relationship("Foto", back_populates="contrato_fotos")


class InquilinoFoto(Base):
    __tablename__ = "inquilino_foto"

    cedula_inquilino = Column(String(100), ForeignKey("inquilino.cedula", ondelete="CASCADE"), primary_key=True)
    id_foto = Column(Integer, ForeignKey("fotos.id", ondelete="CASCADE"), primary_key=True)
    contexto = Column(String(100))

    inquilino = relationship("Inquilino", back_populates="fotos")
    foto = relationship("Foto", back_populates="inquilino_fotos")


# ---------------------------------------------------------
# PAGOS Y MONTOS
# ---------------------------------------------------------

class MontoActual(Base):
    __tablename__ = "montos_actuales"

    contrato_id = Column(Integer, ForeignKey("contrato.id", ondelete="CASCADE"), primary_key=True)
    fecha_ult_act = Column(DateTime, primary_key=True, default=datetime.utcnow)
    monto_mensualidad = Column(Numeric(10, 3))
    estado = Column(Integer)

    contrato = relationship("Contrato", back_populates="montos")


class PagoMensual(Base):
    __tablename__ = "pagos_mensuales"

    id = Column(Integer, primary_key=True, index=True)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    monto_pagado = Column(Numeric(10, 3))
    es_pago_completo = Column(Boolean)
    monto_adeudado_de_este_pago = Column(Numeric(10, 3))
    tipo = Column(Enum(TipoPagoEnum))
    monto_esperado = Column(Numeric(10, 3))
    estado = Column(Integer)
    contrato_id = Column(Integer, ForeignKey("contrato.id", ondelete="CASCADE"))
    inquilino_cedula = Column(String(100), ForeignKey("inquilino.cedula", ondelete="CASCADE"))
    fecha_vence = Column(DateTime)
    mes = Column(Integer)
    anno = Column(Integer)
    detalle = Column(String(500))

    contrato = relationship("Contrato", back_populates="pagos")
    inquilino = relationship("Inquilino", back_populates="pagos")
    fotos = relationship("PagoFoto", back_populates="pago")


class PagoFoto(Base):
    __tablename__ = "pagos_fotos"

    id_pago = Column(Integer, ForeignKey("pagos_mensuales.id", ondelete="CASCADE"), primary_key=True)
    id_foto = Column(Integer, ForeignKey("fotos.id", ondelete="CASCADE"), primary_key=True)
    detalle = Column(String(500))

    pago = relationship("PagoMensual", back_populates="fotos")
    foto = relationship("Foto", back_populates="pagos_fotos")


# ---------------------------------------------------------
# DEVOLUCIÓN DEL DEPÓSITO
# ---------------------------------------------------------

class DevolucionDeposito(Base):
    __tablename__ = "devolucion_deposito"

    contrato_id = Column(Integer, ForeignKey("contrato.id", ondelete="CASCADE"), primary_key=True)
    inquilino_cedula = Column(String(100), ForeignKey("inquilino.cedula", ondelete="CASCADE"), primary_key=True)
    fecha_devolucion = Column(DateTime, primary_key=True, default=datetime.utcnow)
    rebajos_aplicados = Column(String(200))
    monto_original = Column(Numeric(10, 3))
    monto_devuelto = Column(Numeric(10, 3))
    otros_detalles = Column(String(400))
    id_foto = Column(Integer, ForeignKey("fotos.id", ondelete="SET NULL"))

    contrato = relationship("Contrato", back_populates="devoluciones")
    inquilino = relationship("Inquilino", back_populates="devoluciones")
    foto = relationship("Foto", back_populates="devoluciones")
    
from sqlalchemy import UniqueConstraint
import enum

class RolEnum(enum.Enum):
    admin = "admin"
    gestor = "gestor"
    usuario = "usuario"

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (UniqueConstraint("correo", name="uq_usuario_correo"),)

    id = Column(Integer, primary_key=True, index=True)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    clave_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=True)
    p_apellido = Column(String(100), nullable=True)
    s_apellido = Column(String(100), nullable=True)
    celular = Column(String(50), nullable=True)
    rol = Column(Enum(RolEnum), nullable=False, default=RolEnum.usuario)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
