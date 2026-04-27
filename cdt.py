
from datetime import datetime

class CDT:
    def __init__(self, id_cdt, monto_inicial, tasa_anual, fecha_inicio, fecha_vencimiento):
        self.id_cdt = id_cdt
        self.monto_inicial = monto_inicial
        self.tasa_anual = tasa_anual
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento
        self.valor_actual = monto_inicial
        self.activo = True

    def actualizar_valor(self, fecha_actual):
        if not self.activo:
            return

        fecha_inicio_dt = datetime.strptime(self.fecha_inicio, "%Y-%m-%d")
        fecha_actual_dt = datetime.strptime(fecha_actual, "%Y-%m-%d")
        fecha_vencimiento_dt = datetime.strptime(self.fecha_vencimiento, "%Y-%m-%d")

        if fecha_actual_dt <= fecha_inicio_dt:
            self.valor_actual = self.monto_inicial
            return

        fecha_referencia = fecha_actual_dt
        if fecha_actual_dt > fecha_vencimiento_dt:
            fecha_referencia = fecha_vencimiento_dt

        dias = (fecha_referencia - fecha_inicio_dt).days
        tasa_diaria = (1 + self.tasa_anual) ** (1 / 365) - 1

        self.valor_actual = self.monto_inicial * ((1 + tasa_diaria) ** dias)

    def esta_vencido(self, fecha_actual):
        fecha_actual_dt = datetime.strptime(fecha_actual, "%Y-%m-%d")
        fecha_vencimiento_dt = datetime.strptime(self.fecha_vencimiento, "%Y-%m-%d")
        return fecha_actual_dt >= fecha_vencimiento_dt

    def liquidar(self):
        self.activo = False
        return self.valor_actual

    def obtener_estado(self):
        if self.activo:
            return "Activo"
        return "Liquidado