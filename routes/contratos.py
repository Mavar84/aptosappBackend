from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from database import SessionLocal
from security import get_current_user
import models, schemas

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"],
    dependencies=[Depends(get_current_user)]  # 🔒 todos los endpoints requieren login
)

# ---------------------------------------------------------
# Crear contrato
# ---------------------------------------------------------
@router.post("/", response_model=schemas.ContratoResponse)
def crear_contrato(contrato: schemas.ContratoCreate):
    try:
        with SessionLocal() as db:
            nuevo = models.Contrato(**contrato.dict())
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear contrato: {str(e)}")


# ---------------------------------------------------------
# Listar todos los contratos
# ---------------------------------------------------------
@router.get("/", response_model=list[schemas.ContratoResponse])
def listar_contratos():
    try:
        with SessionLocal() as db:
            return db.query(models.Contrato).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar contratos: {str(e)}")


# ---------------------------------------------------------
# Obtener contrato por ID
# ---------------------------------------------------------
@router.get("/{id}", response_model=schemas.ContratoDetalleResponse)
def obtener_contrato(id: int):
    try:
        with SessionLocal() as db:
            contrato = (
                db.query(models.Contrato)
                .options(
                    joinedload(models.Contrato.inquilinos),
                    joinedload(models.Contrato.montos),
                    joinedload(models.Contrato.devoluciones),
                )
                .filter(models.Contrato.id == id)
                .first()
            )
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")
            return contrato
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contrato: {str(e)}")


# ---------------------------------------------------------
# Actualizar contrato
# ---------------------------------------------------------
@router.put("/{id}", response_model=schemas.ContratoResponse)
def actualizar_contrato(id: int, datos: schemas.ContratoCreate):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")

            for campo, valor in datos.dict(exclude_unset=True).items():
                setattr(contrato, campo, valor)

            db.commit()
            db.refresh(contrato)
            return contrato
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar contrato: {str(e)}")


# ---------------------------------------------------------
# Eliminar contrato
# ---------------------------------------------------------
@router.delete("/{id}")
def eliminar_contrato(id: int):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")
            db.delete(contrato)
            db.commit()
            return {"mensaje": "Contrato eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar contrato: {str(e)}")


# ---------------------------------------------------------
# Buscar contratos por apartamento
# ---------------------------------------------------------
@router.get("/apartamento/{id_apto}", response_model=list[schemas.ContratoResponse])
def buscar_por_apartamento(id_apto: int):
    try:
        with SessionLocal() as db:
            return db.query(models.Contrato).filter(models.Contrato.id_apartamento == id_apto).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar contratos por apartamento: {str(e)}")


# ---------------------------------------------------------
# Buscar contratos por inquilino
# ---------------------------------------------------------
@router.get("/inquilino/{cedula}", response_model=list[schemas.ContratoResponse])
def buscar_por_inquilino(cedula: str):
    try:
        with SessionLocal() as db:
            contratos = (
                db.query(models.Contrato)
                .join(models.ContratoInquilino)
                .filter(models.ContratoInquilino.cedula_inquilino == cedula)
                .all()
            )
            return contratos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar contratos por inquilino: {str(e)}")


# ---------------------------------------------------------
# Obtener contrato activo de un apartamento
# ---------------------------------------------------------
@router.get("/activo/{id_apto}", response_model=schemas.ContratoResponse)
def contrato_activo_por_apartamento(id_apto: int):
    try:
        with SessionLocal() as db:
            contrato = (
                db.query(models.Contrato)
                .filter(models.Contrato.id_apartamento == id_apto)
                .filter(models.Contrato.estado == 1)
                .first()
            )
            if not contrato:
                raise HTTPException(status_code=404, detail="No hay contrato activo para este apartamento")
            return contrato
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contrato activo: {str(e)}")


# ---------------------------------------------------------
# Cambiar estado de contrato (activo/inactivo)
# ---------------------------------------------------------
@router.put("/{id}/estado/{nuevo_estado}")
def cambiar_estado_contrato(id: int, nuevo_estado: int):
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")
            contrato.estado = nuevo_estado
            db.commit()
            return {"mensaje": f"Estado del contrato actualizado a {nuevo_estado}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado del contrato: {str(e)}")


# ---------------------------------------------------------
# Historial de montos de un contrato
# ---------------------------------------------------------
@router.get("/{id}/montos", response_model=list[schemas.MontoActualResponse])
def historial_montos_contrato(id: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.MontoActual)
                .filter(models.MontoActual.contrato_id == id)
                .order_by(models.MontoActual.fecha_ult_act.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar montos del contrato: {str(e)}")


# ---------------------------------------------------------
# Pagos realizados en un contrato
# ---------------------------------------------------------
@router.get("/{id}/pagos", response_model=list[schemas.PagoMensualResponse])
def pagos_de_contrato(id: int):
    try:
        with SessionLocal() as db:
            return (
                db.query(models.PagoMensual)
                .filter(models.PagoMensual.contrato_id == id)
                .order_by(models.PagoMensual.fecha_pago.desc())
                .all()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar pagos del contrato: {str(e)}")
# ---------------------------------------------------------
# CRUD para Contrato-Inquilino (relación)
# ---------------------------------------------------------

# Crear relación contrato-inquilino
@router.post("/inquilinos", response_model=schemas.ContratoInquilinoResponse)
def crear_contrato_inquilino(relacion: schemas.ContratoInquilinoCreate):
    try:
        with SessionLocal() as db:
            # Verificar que el contrato existe
            contrato = db.query(models.Contrato).filter(models.Contrato.id == relacion.id_contrato).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")

            # Verificar que el inquilino existe
            inquilino = db.query(models.Inquilino).filter(models.Inquilino.cedula == relacion.cedula_inquilino).first()
            if not inquilino:
                raise HTTPException(status_code=404, detail="Inquilino no encontrado")

            nueva_relacion = models.ContratoInquilino(**relacion.dict())
            db.add(nueva_relacion)
            db.commit()
            db.refresh(nueva_relacion)
            return nueva_relacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear relación contrato-inquilino: {str(e)}")


# Listar todos los inquilinos de un contrato
@router.get("/{id_contrato}/inquilinos", response_model=list[schemas.ContratoInquilinoResponse])
def listar_inquilinos_de_contrato(id_contrato: int):
    try:
        with SessionLocal() as db:
            relaciones = (
                db.query(models.ContratoInquilino)
                .filter(models.ContratoInquilino.id_contrato == id_contrato)
                .all()
            )
            return relaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar inquilinos del contrato: {str(e)}")


# Obtener todos los contratos asociados a un inquilino
@router.get("/inquilino/{cedula_inquilino}/contratos", response_model=list[schemas.ContratoInquilinoResponse])
def listar_contratos_por_inquilino(cedula_inquilino: str):
    try:
        with SessionLocal() as db:
            relaciones = (
                db.query(models.ContratoInquilino)
                .filter(models.ContratoInquilino.cedula_inquilino == cedula_inquilino)
                .all()
            )
            return relaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar contratos del inquilino: {str(e)}")


# Actualizar prioridad de un inquilino dentro de un contrato
@router.put("/{id_contrato}/inquilino/{cedula_inquilino}", response_model=schemas.ContratoInquilinoResponse)
def actualizar_prioridad_inquilino(id_contrato: int, cedula_inquilino: str, datos: schemas.ContratoInquilinoCreate):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.ContratoInquilino)
                .filter(
                    models.ContratoInquilino.id_contrato == id_contrato,
                    models.ContratoInquilino.cedula_inquilino == cedula_inquilino,
                )
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación contrato-inquilino no encontrada")

            if datos.prioridad is not None:
                relacion.prioridad = datos.prioridad

            db.commit()
            db.refresh(relacion)
            return relacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar relación contrato-inquilino: {str(e)}")


# Eliminar relación contrato-inquilino
@router.delete("/{id_contrato}/inquilino/{cedula_inquilino}")
def eliminar_contrato_inquilino(id_contrato: int, cedula_inquilino: str):
    try:
        with SessionLocal() as db:
            relacion = (
                db.query(models.ContratoInquilino)
                .filter(
                    models.ContratoInquilino.id_contrato == id_contrato,
                    models.ContratoInquilino.cedula_inquilino == cedula_inquilino,
                )
                .first()
            )
            if not relacion:
                raise HTTPException(status_code=404, detail="Relación no encontrada")

            db.delete(relacion)
            db.commit()
            return {"mensaje": "Relación contrato-inquilino eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar relación contrato-inquilino: {str(e)}")
# ---------------------------------------------------------
# Generar PDF completo del contrato y devolver en Base64
# ---------------------------------------------------------
from fastapi import Body, HTTPException
from io import BytesIO
import base64
from datetime import datetime
from decimal import Decimal
import io

from database import SessionLocal
import models

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

from PIL import Image as PILImage

# --- utilidades locales (sin setlocale) ---
SPANISH_MONTHS = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def _num_to_words_es(n: int) -> str:
    """Convierte un entero a palabras en español. Intenta usar num2words si está disponible."""
    try:
        from num2words import num2words
        return num2words(n, lang="es")
    except Exception:
        # fallback simple si num2words no está instalada
        return str(n)

def _money_to_words_upper(amount: Decimal | float | int) -> str:
    """Devuelve '₡1.234.000 (<b>UN MILLÓN DOSCIENTOS TREINTA Y CUATRO MIL COLONES</b>)'."""
    amount = Decimal(str(amount or 0)).quantize(Decimal("1."))  # sin decimales
    num = f"₡{int(amount):,}".replace(",", ".")
    palabras = _num_to_words_es(int(amount)).upper()
    return f"{num} (<b>{palabras} COLONES</b>)"

def _id_to_words_upper(idnum: str) -> str:
    """Convierte una cédula como '112240621' a 'UNO UNO DOS DOS CUATRO CERO SEIS DOS UNO' en mayúsculas y negrita."""
    try:
        # Mantiene solo los dígitos
        digits = [c for c in str(idnum) if c.isdigit()]
        if not digits:
            return f"{idnum} (<b>{idnum}</b>)"
        # Mapa de números a palabras
        mapa = {
            "0": "CERO", "1": "UNO", "2": "DOS", "3": "TRES", "4": "CUATRO",
            "5": "CINCO", "6": "SEIS", "7": "SIETE", "8": "OCHO", "9": "NUEVE"
        }
        # Construir texto uno a uno
        texto = " ".join([mapa[d] for d in digits])
        return f"{idnum} (<b>{texto}</b>)"
    except Exception:
        return f"{idnum} (<b>{idnum}</b>)"


def _date_with_words_upper(dt: datetime | None) -> str:
    if not dt:
        return "___ (<b>___</b>)"
    dia = dt.day
    mes = SPANISH_MONTHS.get(dt.month, "")
    anio = dt.year
    fecha_str = f"{dia:02d}/{dt.month:02d}/{anio}"
    dia_w = _num_to_words_es(dia).upper()
    mes_w = mes.upper()
    anio_w = _num_to_words_es(anio).upper()
    return f"{fecha_str} (<b>{dia_w} DE {mes_w} DE {anio_w}</b>)"

def _bold_upper(s: str) -> str:
    return f"<b>{(s or '').upper()}</b>"

# Nota: se asume que existe un APIRouter llamado `router` en el módulo.
@router.post("/{id}/pdf")
def generar_pdf_completo(
    id: int,
    datos: dict = Body(...),
):
    """
    Genera el PDF del contrato con texto completo y datos personalizados y lo devuelve en Base64.
    Cuerpo JSON esperado:
      {
        "propietarios": [{"nombre": "...", "cedula": "...", "calidades": "..."}],
        "fincaInfo": "San José, finca 603918, plano SJ-1356245-2009",
        "inquilinos": [{"nombre": "...", "cedula": "..."}]
      }
    """
    try:
        with SessionLocal() as db:
            contrato = db.query(models.Contrato).filter(models.Contrato.id == id).first()
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato no encontrado")

            # --------- Apartamento por id_apartamento del contrato ----------
            apto = None
            if getattr(contrato, "id_apartamento", None):
                apto = db.query(models.Apartamento).filter(models.Apartamento.id == contrato.id_apartamento).first()

            propietarios = datos.get("propietarios", []) or []
            finca_info = datos.get("fincaInfo", "") or ""
            inquilinos = datos.get("inquilinos", []) or []

            if not propietarios or not finca_info or not inquilinos:
                raise HTTPException(status_code=400, detail="Faltan datos requeridos")

            # -------- Datos del contrato (con defaults seguros) --------
            fecha_inicio_dt = getattr(contrato, "fecha_inicio", None)
            fecha_formal_dt = getattr(contrato, "fecha_formalizacion", None)
            fecha_max_deposito_dt = getattr(contrato, "fecha_maxima_pago_deposito", None)

            fecha_inicio = _date_with_words_upper(fecha_inicio_dt)
            fecha_formalizacion = _date_with_words_upper(fecha_formal_dt)
            fecha_max_deposito = _date_with_words_upper(fecha_max_deposito_dt)

            monto_mensual = getattr(contrato, "monto_mensual_inicial", 0) or 0
            deposito_monto = getattr(contrato, "monto_deposito_inicial", 0) or 0
            monto_mensual_fmt = _money_to_words_upper(monto_mensual)
            deposito_fmt = _money_to_words_upper(deposito_monto)
            monto_estimado_anual_fmt = _money_to_words_upper((Decimal(str(monto_mensual)) * 12))

            dia_pago_mes = getattr(contrato, "dia_pago_mes", None) or "___"
            dia_pago_mes_words = _num_to_words_es(int(dia_pago_mes)).upper() if str(dia_pago_mes).isdigit() else "___"

            # -------- Características del apartamento (de su esquema) --------
            if apto:
                direccion_fisica = getattr(apto, "direccion_fisica", "___")
                num_piso = getattr(apto, "num_piso", "___")
                num_cuartos = getattr(apto, "num_cuartos", "___")
                num_bannos = getattr(apto, "num_bannos", "___")
                num_pilas = getattr(apto, "num_pilas", "___")
                num_salas = getattr(apto, "num_salas", "___")
                num_cocina = getattr(apto, "num_cocina", "___")
                num_comedor = getattr(apto, "num_comedor", "___")
                color_interno = getattr(apto, "color_interno", "___")
                color_externo = getattr(apto, "color_externo", "___")
                num_ventanas = getattr(apto, "num_ventanas", "___")
                tiene_ducha_apto = "sí" if getattr(apto, "tiene_ducha", False) else "no"
                num_220 = getattr(apto, "num_220", "___")
                num_closet = getattr(apto, "num_closet", "___")
                num_mueble_cocina = getattr(apto, "num_mueble_cocina", "___")
            else:
                direccion_fisica = "___"
                num_piso = num_cuartos = num_bannos = num_pilas = num_salas = num_cocina = num_comedor = "___"
                color_interno = color_externo = "___"
                num_ventanas = num_220 = num_closet = num_mueble_cocina = "___"
                tiene_ducha_apto = "___"

            # -------- Parqueo (si está en contrato o en el apto) --------
            tiene_parqueo = (
                getattr(contrato, "tiene_parqueo", None)
                if getattr(contrato, "tiene_parqueo", None) is not None
                else getattr(apto, "tiene_parqueo", False) if apto else False
            )
            texto_parqueo = "El contrato incluye 1 espacio de parqueo asignado." if tiene_parqueo else "El contrato se arrienda sin parqueo asignado."

            # -------- servicios incluidos --------
            agua_incluida = bool(getattr(contrato, "agua_incluida", False))
            luz_incluida = bool(getattr(contrato, "luz_incluida", False))
            internet_incluido = bool(getattr(contrato, "internet_incluido", False))
            cable_incluido = bool(getattr(contrato, "cable_incluido", False))

            # -------- mascotas --------
            cant_mascotas = getattr(contrato, "cantidad_mascotas", 0) or 0
            texto_mascota = (
                f"Se autoriza la tenencia de {cant_mascotas} mascota(s). El arrendatario se compromete a evitar daños, olores, ruidos y a recoger desechos; responderá por todo daño ocasionado."
                if cant_mascotas > 0 else
                "El inmueble se arrienda sin mascotas."
            )

            # personas que habitarán = len(inquilinos)
            cant_personas = len(inquilinos)

            # Texto de propietarios e inquilinos con cédula en número y texto en MAYÚSCULA/NEGRITA
            texto_propietarios = "; ".join(
                [f"{_bold_upper(p['nombre'])}, {p.get('calidades','')}, CÉDULA {_id_to_words_upper(p.get('cedula',''))}" for p in propietarios]
            )
            texto_inquilinos = ", ".join(
                [f"{_bold_upper(i['nombre'])}, CÉDULA {_id_to_words_upper(i.get('cedula',''))}" for i in inquilinos]
            )

            # -------- Construcción del PDF --------
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, title="Contrato de Arrendamiento")
            styles = getSampleStyleSheet()
            estilo_texto = ParagraphStyle("justificado", parent=styles["Normal"], alignment=TA_JUSTIFY, fontSize=11, leading=17)
            estilo_titulo = ParagraphStyle("titulo", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=14, spaceAfter=10)

            contenido = []
            contenido.append(Paragraph("CONTRATO DE ARRENDAMIENTO", estilo_titulo))
            contenido.append(Spacer(1, 10))

            # Intro (manteniendo el texto original y agregando dirección si existe)
            intro = f"""
            Nosotros/as: {texto_propietarios}, dueños de la finca {finca_info}, en adelante conocidos como EL PROPIETARIO,
            y {texto_inquilinos}, en carácter de arrendatario(s), hemos convenido en celebrar el presente CONTRATO DE ARRENDAMIENTO,
            del inmueble sito en {direccion_fisica}, el cual se regirá por la Ley General No. 7527 de Arrendamientos Urbanos y Suburbanos
            y por las siguientes cláusulas:
            """
            contenido.append(Paragraph(intro, estilo_texto))
            contenido.append(Spacer(1, 12))

            # Cláusulas
            clausulas = []

            # 1) Inmueble, piso y ambientes — con TODAS las características del esquema del apartamento
            clausulas.append(
                f"<b>PRIMERA:</b> El propietario da en arriendo al arrendatario la vivienda ubicada en el apartamento correspondiente, "
                f"en el <b>piso {num_piso}</b>, compuesta por <b>{num_cuartos}</b> dormitorio(s), <b>{num_bannos}</b> baño(s), "
                f"sala(s): <b>{num_salas}</b>, comedor(es): <b>{num_comedor}</b>, cocina(s): <b>{num_cocina}</b>, pilas: <b>{num_pilas}</b>, "
                f"clóset(s): <b>{num_closet}</b>, mueble(s) de cocina: <b>{num_mueble_cocina}</b>, <b>{num_ventanas}</b> ventana(s), "
                f"instalación eléctrica 220V: <b>{num_220}</b>, ducha: <b>{tiene_ducha_apto}</b>, color interno <b>{color_interno}</b> y color externo <b>{color_externo}</b>. "
                f"El inmueble se entrega en buen estado."
            )

            # 2) Precio, día de pago y depósito (monto y fecha en texto y número)
            clausulas.append(
                f"<b>SEGUNDA:</b> El precio del alquiler es de {monto_mensual_fmt}, pagadero por adelantado a más tardar el día "
                f"<b>{dia_pago_mes}</b> (<b>{dia_pago_mes_words}</b>) de cada mes. El depósito de garantía es de {deposito_fmt}, cuya "
                f"fecha máxima para pagar el <b>depósito</b> es {fecha_max_deposito}."
            )

            # 2.b) Período de gracia y multa
            clausulas.append(
                "<b>TERCERA:</b> En casos excepcionales y de carácter urgente, se concede un período de gracia de cuatro (4) días; "
                "a partir del quinto día se aplicará una multa de <b>₡1.000</b> diarios."
            )

            # 3) Plazo y aumento anual por inflación
            clausulas.append(
                f"<b>CUARTA:</b> El plazo del contrato es de un (1) año a partir del {fecha_inicio}. Si el arrendatario no desea renovar, deberá "
                "avisar por escrito con un mes de anticipación. A partir del segundo año de arrendamiento se aplicará un aumento anual correspondiente "
                "al porcentaje de inflación, según lo dispone la Ley N.º 7527, sobre el precio inmediato anterior."
            )

            # 4) Mejoras y propiedad de mejoras
            clausulas.append(
                "<b>QUINTA:</b> El arrendatario no podrá realizar mejoras sin autorización expresa del propietario. Si no obstante las realizara, "
                "aún útiles o de lujo, pasarán al vencimiento del plazo o terminación del contrato a formar parte del inmueble arrendado, "
                "sin obligación de pago o indemnización por parte del propietario."
            )

            # 5) Conservación y responsabilidad por daños
            clausulas.append(
                " <b>SEXTA:</b> El arrendatario se compromete a mantener el inmueble en buen estado de conservación y a devolverlo en similares condiciones. "
                "Será responsable por cualquier deterioro, daño o desmejora atribuido a su culpa o negligencia, quedando obligado a indemnizar al propietario, "
                "salvo el normal desgaste por uso racional, el transcurso del tiempo o fuerzas imprevisibles de la naturaleza."
            )

            # 6) Servicios básicos: agua y luz (incluidos o no) + suspensión a 3 días
            if agua_incluida and luz_incluida:
                servicios_txt = ("El contrato incluye el pago de agua y electricidad. "
                                 "El arrendatario deberá hacer uso responsable y eficiente de dichos servicios.")
            elif agua_incluida and not luz_incluida:
                servicios_txt = ("El contrato incluye el pago de agua. La electricidad se cobra por aparte según consumo en kWh registrado y la tarifa oficial del CNFL.")
            elif not agua_incluida and luz_incluida:
                servicios_txt = ("El contrato incluye la electricidad. El agua se cobra por aparte según consumo en m³ registrado y las tarifas de AyA.")
            else:
                servicios_txt = ("El contrato <b>no</b> incluye agua ni electricidad; ambos se cobran por aparte según consumos "
                                 "medidos (m³ para agua y kWh para electricidad) y a la tarifa oficial vigente (AyA y CNFL).")

            clausulas.append(
                "<b>SÉPTIMA:</b> " + servicios_txt +
                " El propietario enviará, días antes del pago, el detalle de consumo: m³ de agua y kWh de electricidad. "
                "Los montos dependen de tarifas oficiales y pueden variar conforme leyes y reglamentos. "
                "Si el arrendatario no paga estos servicios, a partir del <b>tercer</b> día de atraso los mismos podrán ser suspendidos."
            )

            # 7) Internet y cable compartidos (si aplican)
            if internet_incluido or cable_incluido:
                partes = []
                if internet_incluido:
                    partes.append("Internet")
                if cable_incluido:
                    partes.append("televisión por cable")
                lista = " y ".join(partes)
                clausulas.append(
                    f"<b>OCTAVA:</b> Se incluye {lista} de carácter compartido para todos los apartamentos. "
                    "Dado su uso comunitario, puede experimentar intermitencias o caídas ajenas al control del propietario; "
                    "no está pensado para fines profesionales de alta demanda."
                )
            else:
                clausulas.append(
                    "<b>OCTAVA:</b> El contrato no incluye servicios de Internet ni televisión por cable."
                )

            # 8) Sanitarios y fregaderos (mantenimiento/grasas)
            clausulas.append(
                "<b>NOVENA:</b> El arrendatario deberá conservar y dar mantenimiento, por su cuenta, a servicios sanitarios y fregaderos, "
                "manteniéndolos limpios y libres de materiales que puedan obstruirlos. Deberá evitar que grasas u otras sustancias caigan al desagüe, "
                "pues podrían obstruir tuberías y afectar apartamentos adyacentes."
            )

            # 9) Destino y cesión
            clausulas.append(
                "<b>DÉCIMA:</b> El inmueble se destina exclusivamente a casa de habitación. El arrendatario no podrá, bajo ningún concepto, "
                "variar el destino del arriendo ni traspasar la ocupación o uso a terceros, total o parcialmente."
            )
            # 10) Responsabilidad general / accidentes / catastróficos
            clausulas.append(
                "<b>DÉCIMA PRIMERA:</b> El propietario no asume responsabilidad por accidentes de cualquier naturaleza dentro de la propiedad, "
                "ni por daños a propiedad privada, ni por eventos catastróficos o de fuerza mayor."
            )

            # 11) Cobro vía ejecutiva
            clausulas.append(
                "<b>DÉCIMA SEGUNDA:</b> Las sumas de plazo vencido adeudadas por alquileres o cualquier otro concepto podrán cobrarse por la vía ejecutiva, "
                "sin necesidad de requerimiento previo."
            )

            # 12) Incumplimientos y desahucio
            clausulas.append(
                "<b>DÉCIMA TERCERA:</b> El incumplimiento de cualquier obligación faculta a la otra parte para dar por vencido el contrato anticipadamente. "
                "El propietario podrá promover la acción de desahucio cuando corresponda."
            )

            # 13) Tolerancia ≠ modificación
            clausulas.append(
                "<b>DÉCIMA CUARTA:</b> Cualquier concesión eventual del propietario se interpretará como mera tolerancia y no modificará las condiciones pactadas. "
                "Podrá exigirse el cumplimiento estricto en cualquier momento, sin que ello impida acciones legales."
            )

            # 14) Conocimiento de la Ley
            clausulas.append(
                "<b>DÉCIMA QUINTA:</b> Ambas partes declaran conocer la Ley General de Arrendamientos Urbanos y Suburbanos N.º 7527."
            )

            # 15) Inspecciones
            clausulas.append(
                "<b>DÉCIMA SEXTA:</b> El propietario podrá realizar inspecciones periódicas del inmueble con aviso razonable."
            )

            # 16) No fumar / drogas / buenas costumbres
            clausulas.append(
                "<b>DÉCIMA SÉPTIMA:</b> Queda prohibido fumar, consumir drogas o realizar actividades contrarias a la ley o a las buenas costumbres dentro de la propiedad."
            )

            # 17) Ruido y horario de silencio
            clausulas.append(
                "<b>DÉCIMA OCTAVA:</b> Horario de silencio para descanso: de <b>10:00 p.m.</b> a <b>9:00 a.m.</b>, incluidos fines de semana. "
                "Se prohíben ruidos, fiestas o sonidos que perturben a terceros."
            )

            # 18) Parqueo
            clausulas.append(
                f"<b>DÉCIMA NOVENA:</b> {texto_parqueo} El propietario no se hace responsable por daños, pérdidas o robos de bienes dentro del área de parqueo."
            )

            # 19) Mascotas
            clausulas.append(
                f"<b>VIGÉSIMA:</b> {texto_mascota}"
            )

            # 20) Personas que habitarán
            clausulas.append(
                f"<b>VIGÉSIMA PRIMERA:</b> La vivienda será habitada por <b>{cant_personas}</b> persona(s) (según las personas asociadas al contrato)."
            )

            # 21) Depósito: devolución y requisitos (incluye 1 año mínimo)
            clausulas.append(
                "<b>VIGÉSIMA SEGUNDA:</b> Para la devolución del depósito se requiere: "
                "haber residido al menos <b>un (1) año</b> en el inmueble, estar al día con alquileres y servicios, "
                "devolver llaves, y que el inmueble, inventario y mobiliario se encuentren en buen estado (salvo desgaste normal). "
                "Los daños o faltantes podrán deducirse del depósito."
            )

            # 22) Notificaciones
            clausulas.append(
                "<b>VIGÉSIMA TERCERA:</b> Para notificaciones se señalan las direcciones y correos reportados por las partes en este contrato."
            )

            # 23) Estimación del contrato (monto anual, en número y texto)
            clausulas.append(
                f"<b>VIGÉSIMA CUARTA:</b> Se estima el presente contrato en la suma equivalente a un año de alquiler: {monto_estimado_anual_fmt}. "
                "Las partes quedan facultadas para comparecer ante Notario Público a poner <b>Fecha Cierta</b> a este documento."
            )

            # Añadimos todas las cláusulas
            for c in clausulas:
                contenido.append(Paragraph(c, estilo_texto))
                contenido.append(Spacer(1, 8))

            # Cierre con fechas en palabras
            hoy = datetime.now()
            cierre = f"En fe de lo anterior, firmamos de conformidad en San José, a los {_num_to_words_es(hoy.day).upper()} días del mes de {SPANISH_MONTHS[hoy.month].upper()} del {_num_to_words_es(hoy.year).upper()}."
            contenido.append(Paragraph(cierre, estilo_texto))
            contenido.append(Spacer(1, 20))

            # Firmas propietarios
            for p in propietarios:
                contenido.append(Paragraph("______________________________", estilo_texto))
                contenido.append(Paragraph(f"{_bold_upper(p['nombre'])} - CÉDULA: {_id_to_words_upper(p.get('cedula',''))}", estilo_texto))
                contenido.append(Spacer(1, 8))

            # Firmas inquilinos
            for i in inquilinos:
                contenido.append(Paragraph("______________________________", estilo_texto))
                contenido.append(Paragraph(f"{_bold_upper(i['nombre'])} - CÉDULA: {_id_to_words_upper(i.get('cedula',''))}", estilo_texto))
                contenido.append(Spacer(1, 10))

            # ----------------------
            # Fotos de cédulas al final (frente y reverso)
            # ----------------------
            for i in inquilinos:
                ced = i.get("cedula")
                if not ced:
                    continue
                try:
                    fotos = (
                        db.query(models.Foto)
                        .join(models.InquilinoFoto)
                        .filter(models.InquilinoFoto.cedula_inquilino == ced)
                        .all()
                    )
                except Exception as qerr:
                    raise HTTPException(status_code=500, detail=f"Error al listar fotos: {str(qerr)}")

                for f in fotos:
                    print(f)
                    # Frente
                    if getattr(f, "base64_parte1", None):
                        try:
                            contenido.append(Spacer(1, 15))
                            contenido.append(Paragraph(f"Frente de cédula de {_bold_upper(i['nombre'])}", estilo_texto))
                            img_data = base64.b64decode(f.base64_parte1)
                            pil = PILImage.open(io.BytesIO(img_data)).convert("RGB")
                            pil.thumbnail((900, 600))
                            buf = io.BytesIO()
                            pil.save(buf, format="PNG")
                            buf.seek(0)
                            contenido.append(Image(buf, width=300, height=200))
                        except Exception:
                            pass
                    # Reverso
                    if getattr(f, "base64_parte2", None):
                        try:
                            contenido.append(Spacer(1, 10))
                            contenido.append(Paragraph(f"Reverso de cédula de {_bold_upper(i['nombre'])}", estilo_texto))
                            img_data = base64.b64decode(f.base64_parte2)
                            pil = PILImage.open(io.BytesIO(img_data)).convert("RGB")
                            pil.thumbnail((900, 600))
                            buf = io.BytesIO()
                            pil.save(buf, format="PNG")
                            buf.seek(0)
                            contenido.append(Image(buf, width=300, height=200))
                        except Exception:
                            pass

            # Generar PDF
            doc.build(contenido)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
            return {"contrato_id": id, "pdf_base64": pdf_base64}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")
