import csv
from datetime import datetime

from mercado import Mercado
from portafolio import Portafolio


class Simulador:
    def __init__(self):
        self.mercado = Mercado()
        self.portafolio = None

    def leer_entero(self, mensaje, minimo=None, maximo=None):
        while True:
            try:
                valor = int(input(mensaje))

                if minimo is not None and valor < minimo:
                    print(f"El valor debe ser mayor o igual a {minimo}.")
                    continue

                if maximo is not None and valor > maximo:
                    print(f"El valor debe ser menor o igual a {maximo}.")
                    continue

                return valor

            except ValueError:
                print("Entrada inválida. Debe ingresar un número entero.")

    def leer_flotante(self, mensaje, minimo=None):
        while True:
            try:
                valor = float(input(mensaje))

                if minimo is not None and valor < minimo:
                    print(f"El valor debe ser mayor o igual a {minimo}.")
                    continue

                return valor

            except ValueError:
                print("Entrada inválida. Debe ingresar un número.")

    def leer_fecha(self, mensaje):
        while True:
            fecha = input(mensaje).strip()

            try:
                datetime.strptime(fecha, "%Y-%m-%d")
                return fecha
            except ValueError:
                print("Fecha inválida. Use el formato YYYY-MM-DD.")

    def pausar(self):
        input("\nPresione ENTER para continuar...")

    def iniciar(self):
        print("Cargando acciones disponibles...")
        self.mercado.cargar_acciones()

        print("Descargando datos de mercado...")
        self.mercado.descargar_datos()

        capital_inicial = self.leer_flotante("Ingrese el capital inicial en USD: ", 0.01)
        fecha_inicial = self.leer_fecha("Ingrese la fecha inicial de simulación (YYYY-MM-DD): ")

        fecha_ajustada = self.mercado.ajustar_fecha_habil(fecha_inicial)

        if fecha_ajustada is None:
            print("No fue posible iniciar el simulador por falta de datos.")
            return

        if fecha_ajustada != fecha_inicial:
            print(f"La fecha seleccionada no tiene mercado; se usará {fecha_ajustada}.")

        self.portafolio = Portafolio(capital_inicial, fecha_ajustada)
        self.portafolio.registrar_historico(self.mercado)

    def mostrar_menu(self):
        print("\n===== SIMULADOR DE PORTAFOLIO =====")
        print(f"Fecha actual de simulación: {self.portafolio.fecha_actual}")
        print(f"Efectivo disponible: {self.portafolio.efectivo:.2f} USD")
        print(f"Valor total del portafolio: {self.portafolio.valor_total(self.mercado):.2f} USD")
        print("1. Ver acciones disponibles")
        print("2. Comprar acciones")
        print("3. Vender acciones")
        print("4. Comprar CDT")
        print("5. Ver portafolio actual")
        print("6. Ver historial de transacciones")
        print("7. Cambiar fecha de simulación")
        print("8. Ver rentabilidades")
        print("9. Mostrar gráficas")
        print("10. Salir")

    def ver_acciones_disponibles(self):
        print("\n===== ACCIONES DISPONIBLES =====")
        acciones = self.mercado.obtener_acciones()

        for i, accion in enumerate(acciones, start=1):
            ticker = accion.obtener_ticker()
            cierre = self.mercado.obtener_cierre(ticker, self.portafolio.fecha_actual)
            minimo = self.mercado.obtener_minimo(ticker, self.portafolio.fecha_actual)
            maximo = self.mercado.obtener_maximo(ticker, self.portafolio.fecha_actual)
            dividendo = self.mercado.obtener_dividendo(ticker, self.portafolio.fecha_actual)

            print(f"{i}. {accion.obtener_nombre()} ({ticker})")
            print(f"   Cierre: {cierre:.2f} USD")
            print(f"   Mínimo: {minimo:.2f} USD")
            print(f"   Máximo: {maximo:.2f} USD")
            print(f"   Dividendo: {dividendo:.4f}")
            print("")

    def comprar_acciones(self):
        acciones = self.mercado.obtener_acciones()

        print("\n===== COMPRA DE ACCIONES =====")
        for i, accion in enumerate(acciones, start=1):
            print(f"{i}. {accion.obtener_nombre()} ({accion.obtener_ticker()})")

        opcion = self.leer_entero("Seleccione la acción a comprar: ", 1, len(acciones))
        accion = acciones[opcion - 1]
        ticker = accion.obtener_ticker()

        minimo = self.mercado.obtener_minimo(ticker, self.portafolio.fecha_actual)
        maximo = self.mercado.obtener_maximo(ticker, self.portafolio.fecha_actual)
        cierre = self.mercado.obtener_cierre(ticker, self.portafolio.fecha_actual)

        print(f"Cierre: {cierre:.2f} USD")
        print(f"Mínimo del día: {minimo:.2f} USD")
        print(f"Máximo del día: {maximo:.2f} USD")

        precio = self.leer_flotante("Ingrese el precio de la orden: ", 0.01)

        if precio < minimo or precio > maximo:
            print("El precio ingresado está fuera del rango de la jornada.")
            return

        print("1. Comprar por cantidad")
        print("2. Comprar por monto")
        modalidad = self.leer_entero("Seleccione una modalidad: ", 1, 2)

        if modalidad == 1:
            cantidad = self.leer_entero("Ingrese la cantidad de acciones: ", 1)
            exito, mensaje = self.portafolio.comprar_accion(accion, precio, cantidad)
            if exito:
                self.portafolio.registrar_historico(self.mercado)
            print(mensaje)

        else:
            monto = self.leer_flotante("Ingrese el monto máximo a invertir: ", 0.01)
            cantidad = self.portafolio.calcular_cantidad_por_monto(precio, monto)

            if cantidad <= 0:
                print("El monto no alcanza para comprar una acción completa incluyendo comisión.")
                return

            exito, mensaje = self.portafolio.comprar_accion(accion, precio, cantidad)
            if exito:
                self.portafolio.registrar_historico(self.mercado)
            print(mensaje)

            if exito:
                print(f"Cantidad comprada: {cantidad}")

    def vender_acciones(self):
        print("\n===== VENTA DE ACCIONES =====")

        if len(self.portafolio.posiciones_acciones) == 0:
            print("No hay posiciones para vender.")
            return

        for i, posicion in enumerate(self.portafolio.posiciones_acciones, start=1):
            print(f"{i}. {posicion.accion.obtener_nombre()} ({posicion.accion.obtener_ticker()}) - Cantidad: {posicion.obtener_cantidad()}")

        opcion = self.leer_entero("Seleccione la posición a vender: ", 1, len(self.portafolio.posiciones_acciones))

        posicion = self.portafolio.posiciones_acciones[opcion - 1]
        ticker = posicion.accion.obtener_ticker()

        minimo = self.mercado.obtener_minimo(ticker, self.portafolio.fecha_actual)
        maximo = self.mercado.obtener_maximo(ticker, self.portafolio.fecha_actual)
        cierre = self.mercado.obtener_cierre(ticker, self.portafolio.fecha_actual)

        print(f"Cierre: {cierre:.2f} USD")
        print(f"Mínimo del día: {minimo:.2f} USD")
        print(f"Máximo del día: {maximo:.2f} USD")

        precio = self.leer_flotante("Ingrese el precio de venta: ", 0.01)

        if precio < minimo or precio > maximo:
            print("El precio ingresado está fuera del rango de la jornada.")
            return

        cantidad = self.leer_entero("Ingrese la cantidad a vender: ", 1)

        exito, mensaje = self.portafolio.vender_accion(ticker, precio, cantidad)
        if exito:
            self.portafolio.registrar_historico(self.mercado)
        print(mensaje)

    def comprar_cdt(self):
        print("\n===== COMPRA DE CDT =====")

        monto = self.leer_flotante("Ingrese el monto a invertir: ", 0.01)
        tasa_anual = self.leer_flotante("Ingrese la tasa anual (por ejemplo 0.12 para 12%): ", 0.0001)
        fecha_vencimiento = self.leer_fecha("Ingrese la fecha de vencimiento (YYYY-MM-DD): ")

        exito, mensaje = self.portafolio.comprar_cdt(monto, tasa_anual, fecha_vencimiento)
        if exito:
            self.portafolio.registrar_historico(self.mercado)
        print(mensaje)

    def ver_portafolio(self):
        self.portafolio.mostrar_resumen(self.mercado)

    def ver_transacciones(self):
        print("\n===== HISTORIAL DE TRANSACCIONES =====")

        try:
            with open(self.portafolio.archivo_transacciones, mode="r", encoding="utf-8") as archivo:
                lector = list(csv.reader(archivo))

            if len(lector) == 0:
                print("No hay transacciones registradas.")
                return

            for fila in lector:
                print(" | ".join(fila))

        except FileNotFoundError:
            print("No existe el archivo de transacciones.")

    def cambiar_fecha(self):
        nueva_fecha = self.leer_fecha("Ingrese la nueva fecha (YYYY-MM-DD): ")
        fecha_ajustada = self.mercado.ajustar_fecha_habil(nueva_fecha)

        if fecha_ajustada is None:
            print("No hay fechas válidas en los datos descargados.")
            return

        if fecha_ajustada != nueva_fecha:
            print(f"La fecha seleccionada no tiene mercado; se usará {fecha_ajustada}.")

        exito, mensaje = self.portafolio.actualizar_portafolio(self.mercado, fecha_ajustada)
        print(mensaje)

    def ver_rentabilidades(self):
        print("\n===== RENTABILIDADES =====")
        print(f"Rentabilidad acumulada del portafolio: {self.portafolio.rentabilidad_acumulada(self.mercado):.2f}%")
        print(f"Rentabilidad diaria: {self.portafolio.rentabilidad_diaria():.2f}%")
        print(f"Ganancia realizada acumulada: {self.portafolio.ganancia_realizada_acumulada:.2f} USD")

    def mostrar_graficas(self):
        print("Gráficas en desarrollo...")

    def ejecutar(self):
        self.iniciar()

        if self.portafolio is None:
            return

        while True:
            self.mostrar_menu()
            opcion = self.leer_entero("Seleccione una opción: ", 1, 10)

            if opcion == 1:
                self.ver_acciones_disponibles()
            elif opcion == 2:
                self.comprar_acciones()
            elif opcion == 3:
                self.vender_acciones()
            elif opcion == 4:
                self.comprar_cdt()
            elif opcion == 5:
                self.ver_portafolio()
            elif opcion == 6:
                self.ver_transacciones()
            elif opcion == 7:
                self.cambiar_fecha()
            elif opcion == 8:
                self.ver_rentabilidades()
            elif opcion == 9:
                self.mostrar_graficas()
            elif opcion == 10:
                print("Programa finalizado.")
                break

            self.pausar()