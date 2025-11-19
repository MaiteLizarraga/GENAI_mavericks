import sqlite3
from datetime import date
import pandas as pd
import re
import math

def calculo_hipotecario():
    """
    Calcula la hipoteca para el último cliente añadido en la base de datos.
    Determina automáticamente el plazo según ingresos, gastos, importe a financiar y tipo de interés.
    Devuelve cuotas variables y fijas y tablas de amortización.
    """

    # -------------------------------
    # Funciones internas de hipoteca
    # -------------------------------
    def cuota_mensual(P: float, annual_rate_percent: float, years: int) -> float:
        if annual_rate_percent == 0:
            return P / (years * 12)
        r = annual_rate_percent / 100.0 / 12.0
        n = years * 12
        numerator = P * r * (1 + r) ** n
        denominator = (1 + r) ** n - 1
        return numerator / denominator

    def generar_tabla_amortizacion(P: float, annual_rate_percent: float, years: int, start_date: date = None) -> pd.DataFrame:
        if start_date is None:
            start_date = date.today()
        r = annual_rate_percent / 100.0 / 12.0
        n = years * 12
        cuota = cuota_mensual(P, annual_rate_percent, years)
        saldo = P
        rows = []
        for i in range(1, n + 1):
            interes = saldo * r
            amortizacion = cuota - interes
            saldo_nuevo = max(0.0, saldo - amortizacion)
            fecha = start_date + pd.Timedelta(days=30 * i)
            rows.append({
                "mes": i,
                "fecha": fecha.isoformat(),
                "cuota": round(cuota, 2),
                "interes": round(interes, 2),
                "amortizacion": round(amortizacion, 2),
                "saldo": round(saldo_nuevo, 2)
            })
            saldo = saldo_nuevo
            if saldo <= 0:
                break
        return pd.DataFrame(rows)

    def parse_float(valor, default=0.0):
        """Convierte a float limpiando texto, símbolos y comas"""
        if valor is None:
            return default
        if isinstance(valor, (int, float)):
            return float(valor)
        s = str(valor)
        match = re.search(r"[\d,.]+", s)
        if not match:
            return default
        num_str = match.group(0).replace(",", "")
        try:
            return float(num_str)
        except ValueError:
            return default

    def calcular_plazo(P: float, C_max: float, tasa_anual: float) -> int:
        """Calcula el plazo en años según importe, cuota máxima y tasa anual"""
        if C_max <= 0:
            return 1
        if tasa_anual == 0:
            n_meses = P / C_max
        else:
            r = tasa_anual / 100 / 12
            if C_max <= P * r:
                n_meses = 1
            else:
                n_meses = math.log(C_max / (C_max - P * r)) / math.log(1 + r)
        return max(1, round(n_meses / 12))

    # -------------------------------
    # Leer último cliente añadido
    # -------------------------------
    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes ORDER BY rowid DESC LIMIT 1")
    cliente = c.fetchone()
    conn.close()

    if not cliente:
        raise ValueError("No hay clientes en la base de datos")

    # -------------------------------
    # Extraer datos del cliente
    # -------------------------------
    precio = parse_float(cliente["precio_vivienda"])
    entrada = parse_float(cliente["entrada"])
    # importe_financiar = max(0, precio - entrada)
    importe_financiar = parse_float(cliente["importe_a_financiar"])
    ingresos = parse_float(cliente["ingresos_netos_mensuales"])
    gastos = parse_float(cliente["gastos_mensuales_est"])

    # -------------------------------
    # Determinar riesgo y diferencial
    # -------------------------------
    ratio = ingresos / gastos if gastos else 10
    if ratio >= 4:
        diferencial = 0.5
    elif ratio >= 2:
        diferencial = 1.0
    else:
        diferencial = 1.5

    euribor_actual = 2.0
    tasa_variable = euribor_actual + diferencial
    tasa_fija = 3.5

    # -------------------------------
    # Calcular cuota máxima asumible
    # -------------------------------
    cuota_max = max(100, (ingresos - gastos) * 0.33)  # 33% de ingresos netos disponibles

    # -------------------------------
    # Calcular plazos según cuota máxima
    # -------------------------------
    plazo_var = calcular_plazo(importe_financiar, cuota_max, tasa_variable)
    plazo_fix = calcular_plazo(importe_financiar, cuota_max, tasa_fija)

    # -------------------------------
    # Calcular cuotas y tablas
    # -------------------------------
    cuota_var = cuota_mensual(importe_financiar, tasa_variable, plazo_var)
    cuota_fix = cuota_mensual(importe_financiar, tasa_fija, plazo_fix)

    tabla_var = generar_tabla_amortizacion(importe_financiar, tasa_variable, plazo_var)
    tabla_fix = generar_tabla_amortizacion(importe_financiar, tasa_fija, plazo_fix)

    # -------------------------------
    # Devolver resultados
    # -------------------------------
    return {
        "cliente": cliente["nombre_completo"],
        "dni_nie": cliente["dni_nie"],
        "importe_financiar": importe_financiar,
        "plazo_variable": plazo_var,
        "plazo_fijo": plazo_fix,
        "diferencial": diferencial,
        "tasa_variable": tasa_variable,
        "tasa_fija": tasa_fija,
        "cuota_variable": cuota_var,
        "cuota_fija": cuota_fix,
        "tabla_variable": tabla_var,
        "tabla_fija": tabla_fix
    }