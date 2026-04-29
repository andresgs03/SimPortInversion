class Accion:
    def __init__(self, nombre: str, ticker: str) -> None:
        self.nombre = nombre
        self.ticker = ticker

    def obtener_nombre(self) -> str:
        return self.nombre

    def obtener_ticker(self) -> str:
        return self.ticker
