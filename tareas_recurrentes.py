from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import extract
from models import Contrato, PagoMensual, TipoPagoEnum, ContratoInquilino
from database import SessionLocal

def generar_pagos_pendientes():
    print("entra al metodo de generar pagos pendientes")
    hoy = date.today()
    ayer = hoy - timedelta(days=1)

    with SessionLocal() as db:
        contratos_activos = db.query(Contrato).filter(Contrato.estado == 1).all()

        for contrato in contratos_activos:
            if not contrato.dia_pago_mes:
                continue

            # Obtener primer inquilino asociado
            relacion_inquilino = (
                db.query(ContratoInquilino)
                .filter(ContratoInquilino.id_contrato == contrato.id)
                .first()
            )
            cedula_inquilino = relacion_inquilino.cedula_inquilino if relacion_inquilino else "SIN_CEDULA"

            # ---------------------------------------------------------
            # PAGO MENSUALIDAD
            # ---------------------------------------------------------
            if contrato.dia_pago_mes <= ayer.day:
                pago_existente = db.query(PagoMensual).filter(
                    PagoMensual.contrato_id == contrato.id,
                    PagoMensual.tipo == TipoPagoEnum.mensualidad,
                    extract('month', PagoMensual.fecha_pago) == hoy.month,
                    extract('year', PagoMensual.fecha_pago) == hoy.year
                ).first()

                if pago_existente:
                    continue

                pago_anterior = db.query(PagoMensual).filter(
                    PagoMensual.contrato_id == contrato.id,
                    PagoMensual.tipo == TipoPagoEnum.mensualidad
                ).order_by(PagoMensual.fecha_pago.desc()).first()

                monto_esperado = contrato.monto_mensual_inicial or 0

                if pago_anterior and pago_anterior.monto_adeudado_de_este_pago < 0:
                    monto_esperado += abs(pago_anterior.monto_adeudado_de_este_pago)

                fecha_vence = datetime(
                    hoy.year,
                    hoy.month,
                    min(contrato.dia_pago_mes, 28)  # evita errores con meses cortos
                )

                nuevo_pago = PagoMensual(
                    contrato_id=contrato.id,
                    tipo=TipoPagoEnum.mensualidad,
                    fecha_pago=hoy,
                    monto_pagado=0,
                    monto_esperado=monto_esperado,
                    monto_adeudado_de_este_pago=monto_esperado,
                    estado=1,  # pendiente
                    es_pago_completo=False,
                    inquilino_cedula=cedula_inquilino,
                    fecha_vence=fecha_vence,
                    mes=hoy.month,
                    anno=hoy.year,
                    detalle="Pago mensual automático generado",
                )
                db.add(nuevo_pago)
                db.commit()

            # ---------------------------------------------------------
            # PAGOS DE AGUA Y LUZ (si los recibos no están incluidos)
            # ---------------------------------------------------------
            if not getattr(contrato, "recibos_incluidos", True):

                # Pago de agua
                if getattr(contrato, "dia_pago_agua", None) and contrato.dia_pago_agua <= ayer.day:
                    pago_existente_agua = db.query(PagoMensual).filter(
                        PagoMensual.contrato_id == contrato.id,
                        PagoMensual.tipo == TipoPagoEnum.agua,
                        extract('month', PagoMensual.fecha_pago) == hoy.month,
                        extract('year', PagoMensual.fecha_pago) == hoy.year
                    ).first()

                    if not pago_existente_agua:
                        pago_anterior_agua = db.query(PagoMensual).filter(
                            PagoMensual.contrato_id == contrato.id,
                            PagoMensual.tipo == TipoPagoEnum.agua
                        ).order_by(PagoMensual.fecha_pago.desc()).first()

                        monto_esperado_agua = 0
                        if pago_anterior_agua and pago_anterior_agua.monto_adeudado_de_este_pago < 0:
                            monto_esperado_agua += abs(pago_anterior_agua.monto_adeudado_de_este_pago)

                        fecha_vence_agua = datetime(
                            hoy.year,
                            hoy.month,
                            min(contrato.dia_pago_agua, 28)
                        )

                        nuevo_pago_agua = PagoMensual(
                            contrato_id=contrato.id,
                            tipo=TipoPagoEnum.agua,
                            fecha_pago=hoy,
                            monto_pagado=0,
                            monto_esperado=monto_esperado_agua,
                            monto_adeudado_de_este_pago=monto_esperado_agua,
                            estado=1,
                            es_pago_completo=False,
                            inquilino_cedula=cedula_inquilino,
                            fecha_vence=fecha_vence_agua,
                            mes=hoy.month,
                            anno=hoy.year,
                            detalle="Pago de agua generado automáticamente"
                        )
                        db.add(nuevo_pago_agua)
                        db.commit()

                # Pago de luz
                if getattr(contrato, "dia_pago_luz", None) and contrato.dia_pago_luz <= ayer.day:
                    pago_existente_luz = db.query(PagoMensual).filter(
                        PagoMensual.contrato_id == contrato.id,
                        PagoMensual.tipo == TipoPagoEnum.luz,
                        extract('month', PagoMensual.fecha_pago) == hoy.month,
                        extract('year', PagoMensual.fecha_pago) == hoy.year
                    ).first()

                    if not pago_existente_luz:
                        pago_anterior_luz = db.query(PagoMensual).filter(
                            PagoMensual.contrato_id == contrato.id,
                            PagoMensual.tipo == TipoPagoEnum.luz
                        ).order_by(PagoMensual.fecha_pago.desc()).first()

                        monto_esperado_luz = 0
                        if pago_anterior_luz and pago_anterior_luz.monto_adeudado_de_este_pago < 0:
                            monto_esperado_luz += abs(pago_anterior_luz.monto_adeudado_de_este_pago)

                        fecha_vence_luz = datetime(
                            hoy.year,
                            hoy.month,
                            min(contrato.dia_pago_luz, 28)
                        )

                        nuevo_pago_luz = PagoMensual(
                            contrato_id=contrato.id,
                            tipo=TipoPagoEnum.luz,
                            fecha_pago=hoy,
                            monto_pagado=0,
                            monto_esperado=monto_esperado_luz,
                            monto_adeudado_de_este_pago=monto_esperado_luz,
                            estado=1,
                            es_pago_completo=False,
                            inquilino_cedula=cedula_inquilino,
                            fecha_vence=fecha_vence_luz,
                            mes=hoy.month,
                            anno=hoy.year,
                            detalle="Pago de luz generado automáticamente"
                        )
                        db.add(nuevo_pago_luz)
                        db.commit()

            # ---------------------------------------------------------
            # PAGO DE DEPÓSITO
            # ---------------------------------------------------------
            if getattr(contrato, "monto_deposito_inicial", 0):
                fecha_maxima = getattr(contrato, "fecha_maxima_pago_deposito", None)
                fecha_vence_deposito = datetime(hoy.year, hoy.month, 1)

                # --- CASO NORMAL
                if fecha_maxima and hoy <= fecha_maxima.date():
                    pago_existente_deposito = db.query(PagoMensual).filter(
                        PagoMensual.contrato_id == contrato.id,
                        PagoMensual.tipo == TipoPagoEnum.deposito,
                        extract('month', PagoMensual.fecha_pago) == hoy.month,
                        extract('year', PagoMensual.fecha_pago) == hoy.year
                    ).first()

                    if not pago_existente_deposito:
                        pagos_anteriores_deposito = db.query(PagoMensual).filter(
                            PagoMensual.contrato_id == contrato.id,
                            PagoMensual.tipo == TipoPagoEnum.deposito
                        ).order_by(PagoMensual.fecha_pago.desc()).all()

                        if not pagos_anteriores_deposito:
                            monto_a_generar = contrato.monto_deposito_inicial
                        else:
                            monto_total_pagado = sum(p.monto_pagado for p in pagos_anteriores_deposito)
                            monto_a_generar = max((contrato.monto_deposito_inicial or 0) - monto_total_pagado, 0)

                        if monto_a_generar > 0:
                            nuevo_pago_deposito = PagoMensual(
                                contrato_id=contrato.id,
                                tipo=TipoPagoEnum.deposito,
                                fecha_pago=hoy,
                                monto_pagado=0,
                                monto_esperado=monto_a_generar,
                                monto_adeudado_de_este_pago=monto_a_generar,
                                estado=1,
                                es_pago_completo=False,
                                inquilino_cedula=cedula_inquilino,
                                fecha_vence=fecha_vence_deposito,
                                mes=hoy.month,
                                anno=hoy.year,
                                detalle="Pago de depósito inicial generado automáticamente"
                            )
                            db.add(nuevo_pago_deposito)
                            db.commit()

                # --- CASO ATRASADO
                elif fecha_maxima and hoy > fecha_maxima.date():
                    pago_anterior_deposito = db.query(PagoMensual).filter(
                        PagoMensual.contrato_id == contrato.id,
                        PagoMensual.tipo == TipoPagoEnum.deposito
                    ).order_by(PagoMensual.fecha_pago.desc()).first()

                    if pago_anterior_deposito and pago_anterior_deposito.monto_adeudado_de_este_pago < 0:
                        monto_pendiente = abs(pago_anterior_deposito.monto_adeudado_de_este_pago)

                        existe_actual = db.query(PagoMensual).filter(
                            PagoMensual.contrato_id == contrato.id,
                            PagoMensual.tipo == TipoPagoEnum.deposito,
                            extract('month', PagoMensual.fecha_pago) == hoy.month,
                            extract('year', PagoMensual.fecha_pago) == hoy.year
                        ).first()

                        if not existe_actual and monto_pendiente > 0:
                            nuevo_pago_deposito_atrasado = PagoMensual(
                                contrato_id=contrato.id,
                                tipo=TipoPagoEnum.deposito,
                                fecha_pago=hoy,
                                monto_pagado=0,
                                monto_esperado=monto_pendiente,
                                monto_adeudado_de_este_pago=monto_pendiente,
                                estado=1,
                                es_pago_completo=False,
                                inquilino_cedula=cedula_inquilino,
                                fecha_vence=fecha_vence_deposito,
                                mes=hoy.month,
                                anno=hoy.year,
                                detalle="Pago de depósito atrasado generado automáticamente"
                            )
                            db.add(nuevo_pago_deposito_atrasado)
                            db.commit()
