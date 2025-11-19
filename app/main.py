from saludo_lopd_morosidad import saludo_inicial
from slot_filling import obtener_datos_hipoteca
from db_new_clients import init_db
from calculo_hipoteca import calculo_hipotecario
import pandas as pd
import json
from model_loader import llm

def main():
    # Saludo inicial
    saludo_inicial()
    
    init_db()

    # Slot filling / preguntas del modelo
    with open("../data/slots_basicos.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    slots = config["slots"]
    cliente_id, datos = obtener_datos_hipoteca(slots)
    resultado = calculo_hipotecario(cliente_id, datos)
    
    # Mostrar resultados principales
    print("\nResultados de la hipoteca:")
    print(f"Cliente: {resultado['cliente']} ({resultado['dni_nie']})")
    print(f"Importe a financiar: {resultado['importe_financiar']:.2f} €")
    print(f"Cuota mensual tipo variable ({resultado['tasa_variable']:.2f}%): {resultado['cuota_variable']:.2f} €")
    print(f"Tiempo en meses (variable): {resultado['n_meses_variable']} meses")
    print(f"Cuota mensual tipo fijo ({resultado['tasa_fija']:.2f}%): {resultado['cuota_fija']:.2f} €")
    print(f"Tiempo en meses (fijo): {resultado['n_meses_fijo']} meses")

    # ---------------------------
    # Mostrar tabla de amortización anual
    # ---------------------------
    for tipo, tabla in [("Variable", resultado["tabla_variable"]), ("Fijo", resultado["tabla_fija"])]:
        print(f"\nTabla de amortización anual ({tipo}):")
        
        # Convertir a DataFrame si no lo es
        if not isinstance(tabla, pd.DataFrame):
            tabla = pd.DataFrame(tabla)
        
        # Asegurarse de que las columnas numéricas sean float
        for col in ["cuota", "interes", "amortizacion", "saldo"]:
            tabla[col] = tabla[col].astype(float)
        
        # Extraer año
        tabla["año"] = pd.to_datetime(tabla["fecha"]).dt.year
        
        # Agrupar por año
        resumen_anual = tabla.groupby("año").agg({
            "cuota": "sum",
            "interes": "sum",
            "amortizacion": "sum",
            "saldo": "last"
        }).reset_index()
        
        # Imprimir
        print(resumen_anual.to_string(index=False, float_format="{:.2f}".format))


    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Agente: ¡Hasta luego!")
            break

        # Llamada al modelo Groq
        respuesta = llm.invoke(user_input)
        print("Agente:", respuesta.content.strip())

if __name__ == "__main__":
    main()