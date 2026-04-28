import pandas as pd
import yfinance as yf

from accion import Accion

class Mercado:
    def __init__(self):
        self.acciones_disponibles = []
        self.datos_historicos = {}
        self.fecha_inicio = None
        self.fecha_fin = None

    def cargar_acciones(self):
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

    def descargar_datos(self):
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

    def obtener_todas_las_fechas(self):
        fechas = set()

        for ticker in self.datos_historicos:
            datos = self.datos_historicos[ticker]
            if not datos.empty:
                for fecha in datos.index.tolist():
                    fechas.add(fecha)

        fechas = list(fechas)
        fechas.sort()
        return fechas

    def obtener_acciones(self):
        return self.acciones_disponibles

    def ajustar_fecha_habil(self, fecha):
        fechas = self.obtener_todas_las_fechas()

        if len(fechas) == 0:
            return None

        fecha = pd.to_datetime(fecha).strftime("%Y-%m-%d")

        for fecha_disponible in fechas:
            if fecha_disponible >= fecha:
                return fecha_disponible

        return fechas[-1]

    def _ajustar_fecha_para_ticker(self, ticker, fecha):
        if ticker not in self.datos_historicos:
            return None

        datos = self.datos_historicos[ticker]
        if datos.empty:
            return None

        fecha = pd.to_datetime(fecha).strftime("%Y-%m-%d")
        fechas = datos.index.tolist()

        for fecha_disponible in fechas:
            if fecha_disponible >= fecha:
                return fecha_disponible

        return fechas[-1]

    def obtener_cierre(self, ticker, fecha):
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)
        if fecha_ajustada is None:
            return 0.0
        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "Close"])

    def obtener_minimo(self, ticker, fecha):
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)
        if fecha_ajustada is None:
            return 0.0
        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "Low"])

    def obtener_maximo(self, ticker, fecha):
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)
        if fecha_ajustada is None:
            return 0.0
        return float(self.datos_historicos[ticker].loc[fecha_ajustada, "High"])

    def obtener_dividendo(self, ticker, fecha):
        fecha_ajustada = self._ajustar_fecha_para_ticker(ticker, fecha)
        if fecha_ajustada is None:
            return 0.0
        datos = self.datos_historicos[ticker]
        if "Dividends" not in datos.columns:
            return 0.0
        return float(datos.loc[fecha_ajustada, "Dividends"])

    def obtener_fechas_entre(self, fecha_inicio, fecha_fin):
        fechas = self.obtener_todas_las_fechas()
        fecha_inicio = pd.to_datetime(fecha_inicio).strftime("%Y-%m-%d")
        fecha_fin = pd.to_datetime(fecha_fin).strftime("%Y-%m-%d")

        resultado = []
        for fecha in fechas:
            if fecha_inicio < fecha <= fecha_fin:
                resultado.append(fecha)

        return resultado
