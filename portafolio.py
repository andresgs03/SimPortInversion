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

        ingreso_bruto = precio * cantidad
        comision = self._calcular_comision(ingreso_bruto)
        ingreso_neto = ingreso_bruto - comision

        exito = posicion.vender(cantidad)

        if not exito:
            return False, "No fue posible vender la cantidad indicada."

        self.efectivo += ingreso_neto
        self.comisiones_acumuladas += comision

        if posicion.obtener_cantidad() == 0:
            self.posiciones_acciones.remove(posicion)

        self.registrar_transaccion({
            "fecha": self.fecha_actual,
            "tipo_operacion": "venta_accion",
            "activo": ticker,
            "ticker": ticker,
            "cantidad": cantidad,
            "precio": precio,
            "monto": ingreso_bruto,
            "comision": comision,
            "efectivo_resultante": self.efectivo,
            "detalle": "Venta de acciones"
        })

        return True, "Venta realizada correctamente."

def comprar_cdt(self, monto, tasa_anual, fecha_vencimiento):
        if monto <= 0:
            return False, "El monto debe ser mayor que cero."

        if tasa_anual <= 0:
            return False, "La tasa anual debe ser mayor que cero."

        # --- FIX: VALIDACIÓN DE FECHA ---
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