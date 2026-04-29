import csv
import os
from datetime import datetime

from posicion_accion import PosicionAccion
from cdt import CDT


class Portafolio:
    def __init__(self, capital_inicial, fecha_actual):
        self.capital_inicial = capital_inicial
        self.efectivo = capital_inicial
        self.posiciones_acciones = []
        self.cdts = []
        self.comisiones_acumuladas = 0.0
        self.dividendos_recibidos_acumulados = 0.0
        self.ganancia_realizada_acumulada = 0.0
        self.fecha_actual = fecha_actual
        self.historico = []
        self.archivo_transacciones = "transacciones.csv"
        self.siguiente_id_cdt = 1

        self._inicializar_archivo_transacciones()

    def _inicializar_archivo_transacciones(self):
        if not os.path.exists(self.archivo_transacciones):
            with open(self.archivo_transacciones, mode="w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([
                    "fecha", "tipo_operacion", "activo", "ticker", "cantidad",
                    "precio", "monto", "comision", "efectivo_resultante", "detalle"
                ])

    def _calcular_comision(self, monto):
        comision = monto * 0.005
        if comision < 1:
            comision = 1.0
        return comision

    def _buscar_posicion(self, ticker):
        for posicion in self.posiciones_acciones:
            if posicion.accion.obtener_ticker() == ticker:
                return posicion
        return None

    def comprar_accion(self, accion, precio, cantidad):
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que cero."

        costo_bruto = precio * cantidad
        comision = self._calcular_comision(costo_bruto)
        costo_total = costo_bruto + comision

        if costo_total > self.efectivo:
            return False, "No hay suficiente efectivo para completar la compra."

        posicion = self._buscar_posicion(accion.obtener_ticker())

        if posicion is None:
            posicion = PosicionAccion(accion)
            self.posiciones_acciones.append(posicion)

        posicion.comprar(cantidad, costo_total)

        self.efectivo -= costo_total
        self.comisiones_acumuladas += comision

        self.registrar_transaccion({
            "fecha": self.fecha_actual,
            "tipo_operacion": "compra_accion",
            "activo": accion.obtener_nombre(),
            "ticker": accion.obtener_ticker(),
            "cantidad": cantidad,
            "precio": precio,
            "monto": costo_bruto,
            "comision": comision,
            "efectivo_resultante": self.efectivo,
            "detalle": "Compra de acciones"
        })

        return True, "Compra realizada correctamente."

    def calcular_cantidad_por_monto(self, precio, monto):
        if precio <= 0 or monto <= 0:
            return 0

        cantidad = int(monto / precio)

        while cantidad > 0:
            costo_bruto = precio * cantidad
            comision = self._calcular_comision(costo_bruto)
            costo_total = costo_bruto + comision

            if costo_total <= monto and costo_total <= self.efectivo:
                return cantidad

            cantidad -= 1

        return 0

    def vender_accion(self, ticker, precio, cantidad):
        posicion = self._buscar_posicion(ticker)

        if posicion is None:
            return False, "No existe una posición en esa acción."

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que cero."

        if cantidad > posicion.obtener_cantidad():
            return False, "La cantidad a vender supera la posición disponible."

        nombre_activo = posicion.accion.obtener_nombre()
        ingreso_bruto = precio * cantidad
        comision = self._calcular_comision(ingreso_bruto)
        ingreso_neto = ingreso_bruto - comision

        exito, costo_retirado = posicion.vender(cantidad)

        if not exito:
            return False, "No fue posible vender la cantidad indicada."

        ganancia_realizada = ingreso_neto - costo_retirado
        self.ganancia_realizada_acumulada += ganancia_realizada

        self.efectivo += ingreso_neto
        self.comisiones_acumuladas += comision

        if posicion.obtener_cantidad() == 0:
            self.posiciones_acciones.remove(posicion)

        self.registrar_transaccion({
            "fecha": self.fecha_actual,
            "tipo_operacion": "venta_accion",
            "activo": nombre_activo,
            "ticker": ticker,
            "cantidad": cantidad,
            "precio": precio,
            "monto": ingreso_bruto,
            "comision": comision,
            "efectivo_resultante": self.efectivo,
            "detalle": f"Venta de {cantidad} acciones a {precio:.2f} USD | Ganancia realizada: {ganancia_realizada:.2f} USD"
        })

        return True, "Venta realizada correctamente."

    def comprar_cdt(self, monto, tasa_anual, fecha_vencimiento):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."

        if tasa_anual <= 0:
            return False, "La tasa anual debe ser mayor que cero."

        try:
            fecha_actual_dt = datetime.strptime(self.fecha_actual, "%Y-%m-%d")
            fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        except ValueError:
            return False, "La fecha de vencimiento no tiene un formato válido."

        if fecha_vencimiento_dt <= fecha_actual_dt:
            return False, "La fecha de vencimiento debe ser posterior a la fecha actual del simulador."

        if monto > self.efectivo:
            return False, "No hay suficiente efectivo para comprar el CDT."

        nuevo_cdt = CDT(
            self.siguiente_id_cdt,
            monto,
            tasa_anual,
            self.fecha_actual,
            fecha_vencimiento
        )

        self.cdts.append(nuevo_cdt)
        self.siguiente_id_cdt += 1
        self.efectivo -= monto

        self.registrar_transaccion({
            "fecha": self.fecha_actual,
            "tipo_operacion": "compra_cdt",
            "activo": "CDT",
            "ticker": "CDT",
            "cantidad": 1,
            "precio": 0,
            "monto": monto,
            "comision": 0,
            "efectivo_resultante": self.efectivo,
            "detalle": f"Tasa anual: {tasa_anual}, vencimiento: {fecha_vencimiento}"
        })

        return True, "CDT comprado correctamente."

    def aplicar_dividendos(self, mercado, fecha_anterior, nueva_fecha):
        fechas = mercado.obtener_fechas_entre(fecha_anterior, nueva_fecha)

        for fecha in fechas:
            for posicion in self.posiciones_acciones:
                ticker = posicion.accion.obtener_ticker()
                dividendo = mercado.obtener_dividendo(ticker, fecha)

                if dividendo > 0:
                    valor_recibido = dividendo * posicion.obtener_cantidad()
                    self.efectivo += valor_recibido
                    self.dividendos_recibidos_acumulados += valor_recibido
                    posicion.agregar_dividendo(valor_recibido)

                    self.registrar_transaccion({
                        "fecha": fecha,
                        "tipo_operacion": "dividendo",
                        "activo": posicion.accion.obtener_nombre(),
                        "ticker": ticker,
                        "cantidad": posicion.obtener_cantidad(),
                        "precio": dividendo,
                        "monto": valor_recibido,
                        "comision": 0,
                        "efectivo_resultante": self.efectivo,
                        "detalle": "Pago de dividendo"
                    })

    def liquidar_cdts(self):
        for cdt in self.cdts:
            if cdt.activo:
                cdt.actualizar_valor(self.fecha_actual)

                if cdt.esta_vencido(self.fecha_actual):
                    valor_liquidado = cdt.liquidar()
                    self.efectivo += valor_liquidado

                    self.registrar_transaccion({
                        "fecha": self.fecha_actual,
                        "tipo_operacion": "liquidacion_cdt",
                        "activo": "CDT",
                        "ticker": "CDT",
                        "cantidad": 1,
                        "precio": 0,
                        "monto": valor_liquidado,
                        "comision": 0,
                        "efectivo_resultante": self.efectivo,
                        "detalle": f"Liquidación automática CDT #{cdt.id_cdt}"
                    })

    def actualizar_portafolio(self, mercado, nueva_fecha):
        fecha_ajustada = mercado.ajustar_fecha_habil(nueva_fecha)

        if fecha_ajustada is None:
            return False, "No se encontraron fechas hábiles disponibles."

        if fecha_ajustada < self.fecha_actual:
            return False, "Solo se permite avanzar a fechas iguales o posteriores a la actual."

        fecha_anterior = self.fecha_actual
        self.fecha_actual = fecha_ajustada

        self.aplicar_dividendos(mercado, fecha_anterior, self.fecha_actual)

        for cdt in self.cdts:
            if cdt.activo:
                cdt.actualizar_valor(self.fecha_actual)

        self.liquidar_cdts()
        self.registrar_historico(mercado)

        return True, f"Portafolio actualizado a la fecha {self.fecha_actual}."

    def valor_acciones(self, mercado):
        total = 0.0
        for posicion in self.posiciones_acciones:
            ticker = posicion.accion.obtener_ticker()
            precio = mercado.obtener_cierre(ticker, self.fecha_actual)
            total += posicion.valor_actual(precio)
        return total

    def valor_cdts(self):
        total = 0.0
        for cdt in self.cdts:
            if cdt.activo:
                total += cdt.valor_actual
        return total

    def valor_total(self, mercado):
        return self.efectivo + self.valor_acciones(mercado) + self.valor_cdts()

    def rentabilidad_acumulada(self, mercado):
        if self.capital_inicial <= 0:
            return 0.0
        return ((self.valor_total(mercado) - self.capital_inicial) / self.capital_inicial) * 100

    def rentabilidad_diaria(self):
        if len(self.historico) < 2:
            return 0.0

        valor_hoy = self.historico[-1]["valor_total"]
        valor_ayer = self.historico[-2]["valor_total"]

        if valor_ayer == 0:
            return 0.0

        return ((valor_hoy - valor_ayer) / valor_ayer) * 100

    def composicion(self, mercado):
        return {
            "Efectivo": self.efectivo,
            "Acciones": self.valor_acciones(mercado),
            "CDTs": self.valor_cdts()
        }

    def registrar_historico(self, mercado):
        self.historico.append({
            "fecha": self.fecha_actual,
            "valor_total": self.valor_total(mercado),
            "efectivo": self.efectivo,
            "acciones": self.valor_acciones(mercado),
            "cdts": self.valor_cdts()
        })

    def registrar_transaccion(self, datos):
        with open(self.archivo_transacciones, mode="a", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([
                datos["fecha"], datos["tipo_operacion"], datos["activo"], datos["ticker"],
                datos["cantidad"], datos["precio"], datos["monto"], datos["comision"],
                datos["efectivo_resultante"], datos["detalle"]
            ])

    def mostrar_resumen(self, mercado):
        print("\n===== RESUMEN DEL PORTAFOLIO =====")
        print(f"Fecha actual: {self.fecha_actual}")
        print(f"Capital inicial: {self.capital_inicial:.2f} USD")
        print(f"Efectivo disponible: {self.efectivo:.2f} USD")
        print(f"Valor en acciones: {self.valor_acciones(mercado):.2f} USD")
        print(f"Valor en CDTs: {self.valor_cdts():.2f} USD")
        print(f"Valor total del portafolio: {self.valor_total(mercado):.2f} USD")
        print(f"Comisiones acumuladas: {self.comisiones_acumuladas:.2f} USD")
        print(f"Dividendos recibidos acumulados: {self.dividendos_recibidos_acumulados:.2f} USD")
        print(f"Ganancia realizada acumulada: {self.ganancia_realizada_acumulada:.2f} USD")

        print("\n--- POSICIONES EN ACCIONES ---")
        if len(self.posiciones_acciones) == 0:
            print("No hay posiciones en acciones.")
        else:
            encabezado = (
                f"{'Activo':<12}"
                f"{'Ticker':<14}"
                f"{'Cant.':>8}"
                f"{'Precio':>12}"
                f"{'Valor':>14}"
                f"{'Costo':>14}"
                f"{'Dividendos':>14}"
                f"{'Rentab.%':>12}"
            )
            print(encabezado)
            print("-" * len(encabezado))

            for posicion in self.posiciones_acciones:
                ticker = posicion.accion.obtener_ticker()
                precio = mercado.obtener_cierre(ticker, self.fecha_actual)

                print(
                    f"{posicion.accion.obtener_nombre():<12}"
                    f"{ticker:<14}"
                    f"{posicion.obtener_cantidad():>8}"
                    f"{precio:>12.2f}"
                    f"{posicion.valor_actual(precio):>14.2f}"
                    f"{posicion.obtener_costo_total():>14.2f}"
                    f"{posicion.dividendos_acumulados:>14.2f}"
                    f"{posicion.rentabilidad(precio):>12.2f}"
                )

        print("\n--- CDTs ---")
        if len(self.cdts) == 0:
            print("No hay CDTs registrados.")
        else:
            encabezado_cdt = (
                f"{'ID':<6}"
                f"{'Monto Inicial':>15}"
                f"{'Tasa':>10}"
                f"{'Inicio':>14}"
                f"{'Vencimiento':>14}"
                f"{'Valor Actual':>16}"
                f"{'Estado':>12}"
            )
            print(encabezado_cdt)
            print("-" * len(encabezado_cdt))

            for cdt in self.cdts:
                print(
                    f"{cdt.id_cdt:<6}"
                    f"{cdt.monto_inicial:>15.2f}"
                    f"{cdt.tasa_anual:>10.4f}"
                    f"{cdt.fecha_inicio:>14}"
                    f"{cdt.fecha_vencimiento:>14}"
                    f"{cdt.valor_actual:>16.2f}"
                    f"{cdt.obtener_estado():>12}"
                )