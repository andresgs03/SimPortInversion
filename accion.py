class Accion:
    def __init__(self, nombre, ticker):
        self.nombre = nombre
        self.ticker = ticker

    def obtener_nombre(self):
        return self.nombre

    def obtener_ticker(self):
        return self.ticker
