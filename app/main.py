import time
from saludo_inicial import saludo_inicial
from gdpr import solicitar_consentimiento_gdpr
from morosidad import solicitar_consentimiento_morosos
from slot_filling import iniciar_slot_filling_json
from calculo_hipoteca import calculo_hipotecario
import pandas as pd

def main():
    # Saludo inicial
    prompts = saludo_inicial()
    
    time.sleep(1.5)

    # Solicitar consentimiento GDPR
    if not solicitar_consentimiento_gdpr():
        return  # Termina el programa si el usuario no consiente
    
    if not solicitar_consentimiento_morosos():
        return # Termina el programa si el usuario no consiente

    # Slot filling / preguntas guiadas
    iniciar_slot_filling_json(prompts)
    
    # Calculo de la hipoteca
    resultado = calculo_hipotecario()
    
    # Mostrar resultados principales
    print("\nResultados de la hipoteca:")
    print(f"Cliente: {resultado['cliente']} ({resultado['dni_nie']})")
    print(f"Importe a financiar: {resultado['importe_financiar']:.2f} €")
    print(f"Cuota mensual tipo variable ({resultado['tasa_variable']:.2f}%): {resultado['cuota_variable']:.2f} €")
    print(f"Cuota mensual tipo fijo ({resultado['tasa_fija']:.2f}%): {resultado['cuota_fija']:.2f} €")

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


if __name__ == "__main__":
    main()