import pandas as pd
import yfinance as yf

from accion import Accion


class Mercado:
    def __init__(self) -> None:
        self.acciones_disponibles: list[Accion] = []
        self.datos_historicos: dict[str, pd.DataFrame] = {}
        self.fecha_inicio: str | None = None
        self.fecha_fin: str | None = None

    def cargar_acciones(self) -> None:
        self.acciones_disponibles = [
            Accion("GEB", "GEB.CL"),
            Accion("PFCIBEST", "PFCIBEST.CL"),
            Accion("PFAVAL", "PFAVAL.CL"),
            Accion("ISA", "ISA.CL"),
            Accion("ECOPETROL", "ECOPETROL.CL"),
            Accion("INTC", "INTC"),
            Accion("MU", "MU"),
            Accion("NVDA", "NVDA"),
            Accion("TSM", "TSM"),
            Accion("AMZN", "AMZN"),
        ]

    def descargar_datos(self) -> None:
        for accion in self.acciones_disponibles:
            ticker = accion.obtener_ticker()

            try:
                historial = yf.Ticker(ticker).history(period="6mo", auto_adjust=False, actions=True)

                if historial.empty:
                    self.datos_historicos[ticker] = pd.DataFrame()
                    continue

                historial.index = pd.to_datetime(historial.index).strftime("%Y-%m-%d")
                self.datos_historicos[ticker] = historial

            except Exception:
                self.datos_historicos[ticker] = pd.DataFrame()

        fechas = self.obtener_todas_las_fechas()
        if len(fechas) > 0:
            self.fecha_inicio = fechas[0]
            self.fecha_fin = fechas[-1]

    def obtener_todas_las_fechas(self) -> list[str]:
        fechas = set()

        for ticker in self.datos_historicos:
            datos = self.datos_historicos[ticker]
            if not datos.empty:
                for fecha in datos.index.tolist():
                    fechas.add(fecha)

        fechas_ordenadas = list(fechas)
        fechas_ordenadas.sort()
        return fechas_ordenadas

    def obtener_acciones(self) -> list[Accion]:
        return self.acciones_disponibles

    def ajustar_fecha_habil(self, fecha: str) -> str | None:
        fechas = self.obtener_todas_las_fechas()

        if len(fechas) == 0:
            return None

        fecha = pd.to_datetime(fecha).strftime("%Y-%m-%d")

        candidata = None
        for fecha_disponible in fechas:
            if fecha_disponible <= fecha:
                candidata = fecha_disponible
            else:
                break

        if candidata is None:
            return fechas[0]

        return candidata

    def _ajustar_fecha_para_ticker(self, ticker: str, fecha: str) -> str | None:
        if ticker not in self.datos_historicos:
            return None

        datos = self.datos_historicos[ticker]
        if datos.empty:
            return None

        fecha = pd.to_datetime(fecha).strftime("%Y-%m-%d")
        fechas = datos.index.tolist()

        candidata = None
        for fecha_disponible in fechas:
            if fecha_disponible <= fecha:
                candidata = fecha_disponible
            else:
                break

        if candidata is None:
            return fechas[0]

        return candidata

    def obtener_cierre(self, ticker: str, fecha: str) -> float:
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)

        if fecha_ajustada is None:
            return 0.0

        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "Close"])

    def obtener_minimo(self, ticker: str, fecha: str) -> float:
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)

        if fecha_ajustada is None:
            return 0.0

        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "Low"])

    def obtener_maximo(self, ticker: str, fecha: str) -> float:
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)

        if fecha_ajustada is None:
            return 0.0

        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "High"])

    def obtener_dividendo(self, ticker: str, fecha: str) -> float:
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)

        if fecha_ajustada is None:
            return 0.0

        datos = self.datos_historicos[ticker]

        if "Dividends" not in datos.columns:
            return 0.0

        return float(datos.loc[fecha_ajustada, "Dividends"])

    def obtener_fechas_entre(self, fecha_inicio: str, fecha_fin: str) -> list[str]:
        fechas = self.obtener_todas_las_fechas()

        fecha_inicio = pd.to_datetime(fecha_inicio).strftime("%Y-%m-%d")
        fecha_fin = pd.to_datetime(fecha_fin).strftime("%Y-%m-%d")

        resultado = []
        for fecha in fechas:
            if fecha_inicio < fecha <= fecha_fin:
                resultado.append(fecha)

        return resultado
