class PosicionAccion:
    def __init__(self, accion) -> None:
        self.accion = accion
        self.cantidad = 0
        self.costo_total = 0.0
        self.dividendos_acumulados = 0.0

    def comprar(self, cantidad: int, costo: float) -> None:
        self.cantidad += cantidad
        self.costo_total += costo

    def vender(self, cantidad: int) -> tuple[bool, float]:
        if cantidad > self.cantidad or cantidad <= 0:
            return False, 0.0

        if self.cantidad > 0:
            costo_promedio = self.costo_total / self.cantidad
            costo_retirado = costo_promedio * cantidad
        else:
            costo_retirado = 0.0

        self.costo_total -= costo_retirado
        self.cantidad -= cantidad

        if self.cantidad == 0:
            self.costo_total = 0.0

        return True, costo_retirado

    def agregar_dividendo(self, valor: float) -> None:
        self.dividendos_acumulados += valor

    def valor_actual(self, precio_cierre: float) -> float:
        return self.cantidad * precio_cierre

    def rentabilidad(self, precio_cierre: float) -> float:
        if self.costo_total <= 0:
            return 0.0

        valor = self.valor_actual(precio_cierre)
        return ((valor + self.dividendos_acumulados - self.costo_total) / self.costo_total) * 100

    def obtener_cantidad(self) -> int:
        return self.cantidad

    def obtener_costo_total(self) -> float:
        return self.costo_total
