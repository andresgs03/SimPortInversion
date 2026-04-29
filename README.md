# Simulador de Portafolio de Inversión

Simulador financiero desarrollado en Python para gestionar y monitorear la rentabilidad de un portafolio diversificado, incluyendo renta variable mediante acciones descargadas desde Yahoo Finance y renta fija mediante CDTs.

## Características principales

- Consulta de precios de cierre, mínimo y máximo usando `yfinance`.
- Universo fijo de 10 acciones.
- Compra y venta de acciones con validación de precio dentro del rango diario.
- Comisión del bróker del 0.5% con mínimo de 1 USD.
- Compra de CDTs con valorización diaria y fecha de vencimiento real.
- Liquidación automática de CDTs vencidos.
- Registro de transacciones en archivo CSV.
- Cálculo de rentabilidad acumulada, rentabilidad diaria y ganancia realizada.
- Manejo de dividendos cuando existen en los datos descargados.
- Gráficas de evolución, rentabilidad y composición del portafolio.

## Acciones disponibles

- GEB.CL
- PFCIBEST.CL
- PFAVAL.CL
- ISA.CL
- ECOPETROL.CL
- INTC
- MU
- NVDA
- TSM
- AMZN

## Arquitectura UML

![Diagrama UML](img/uml_portafolio.png)

## Instalación

Instalar las dependencias necesarias:

```bash
pip install -r requirements.txt
python main.py
