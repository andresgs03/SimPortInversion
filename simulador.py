import csv
from mercado import Mercado
from portafolio import Portafolio

class Simulador:
    def __init__(self):
        self.mercado = Mercado()
        self.portafolio = None

    def iniciar(self):
        print("Cargando acciones disponibles...")
        self.mercado.cargar_acciones()

        print("Descargando datos de mercado...")
        self.mercado.descargar_datos()

        capital_inicial = float(input("Ingrese el capital inicial en USD: "))
        fecha_inicial = input("Ingrese la fecha inicial de simulación (YYYY-MM-DD): ")

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
            print(f"{i}. {accion.obtener_nombre()} ({ticker}) - Cierre: {cierre:.2f} USD")

    def comprar_acciones(self):
        acciones = self.mercado.obtener_acciones()
        print("\n===== COMPRA DE ACCIONES =====")
        for i, accion in enumerate(acciones, start=1):
            print(f"{i}. {accion.obtener_nombre()} ({accion.obtener_ticker()})")

        opcion = int(input("Seleccione la acción a comprar: "))
        accion = acciones[opcion - 1]
        ticker = accion.obtener_ticker()

        cierre = self.mercado.obtener_cierre(ticker, self.portafolio.fecha_actual)
        print(f"Cierre: {cierre:.2f} USD")

        precio = float(input("Ingrese el precio de la orden: "))
        cantidad = int(input("Ingrese la cantidad de acciones: "))
        
        exito, mensaje = self.portafolio.comprar_accion(accion, precio, cantidad)
        print(mensaje)

    def vender_acciones(self):
        print("\n===== VENTA DE ACCIONES =====")
        if len(self.portafolio.posiciones_acciones) == 0:
            print("No hay posiciones para vender.")
            return

        for i, posicion in enumerate(self.portafolio.posiciones_acciones, start=1):
            print(f"{i}. {posicion.accion.obtener_nombre()} ({posicion.accion.obtener_ticker()}) - Cantidad: {posicion.obtener_cantidad()}")

        opcion = int(input("Seleccione la posición a vender: "))
        posicion = self.portafolio.posiciones_acciones[opcion - 1]
        ticker = posicion.accion.obtener_ticker()

        precio = float(input("Ingrese el precio de venta: "))
        cantidad = int(input("Ingrese la cantidad a vender: "))
        
        exito, mensaje = self.portafolio.vender_accion(ticker, precio, cantidad)
        print(mensaje)

    def comprar_cdt(self):
        print("\n===== COMPRA DE CDT =====")
        monto = float(input("Ingrese el monto a invertir: "))
        tasa_anual = float(input("Ingrese la tasa anual (por ejemplo 0.12 para 12%): "))
        fecha_vencimiento = input("Ingrese la fecha de vencimiento (YYYY-MM-DD): ")

        exito, mensaje = self.portafolio.comprar_cdt(monto, tasa_anual, fecha_vencimiento)
        print(mensaje)

    def ver_portafolio(self):
        self.portafolio.mostrar_resumen(self.mercado)

    def ver_transacciones(self):
        print("\n===== HISTORIAL DE TRANSACCIONES =====")
        try:
            with open(self.portafolio.archivo_transacciones, mode="r", encoding="utf-8") as archivo:
                lector = csv.reader(archivo)
                for fila in lector:
                    print(" | ".join(fila))
        except FileNotFoundError:
            print("No existe el archivo de transacciones.")

    def cambiar_fecha(self):
        nueva_fecha = input("Ingrese la nueva fecha (YYYY-MM-DD): ")
        fecha_ajustada = self.mercado.ajustar_fecha_habil(nueva_fecha)

        if fecha_ajustada is None:
            print("No hay fechas válidas en los datos descargados.")
            return

        exito, mensaje = self.portafolio.actualizar_portafolio(self.mercado, fecha_ajustada)
        print(mensaje)

    def ver_rentabilidades(self):
        print("\n===== RENTABILIDADES =====")
        print(f"Rentabilidad acumulada del portafolio: {self.portafolio.rentabilidad_acumulada(self.mercado):.2f}%")
        print(f"Rentabilidad diaria: {self.portafolio.rentabilidad_diaria():.2f}%")

    def mostrar_graficas(self):
        print("Función de gráficas en desarrollo...")

    def ejecutar(self):
        self.iniciar()
        if self.portafolio is None:
            return

        while True:
            self.mostrar_menu()
            opcion = int(input("Seleccione una opción: "))

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