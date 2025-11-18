import sqlite3
from validations import validar_con_modelo
from slot_loader import cargar_slots

def iniciar_slot_filling_json(prompts):
    slots, _ = cargar_slots()
    form_data = {}

    # Conectar SQLite
    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row  # <- Devuelve diccionarios
    c = conn.cursor()

    # Crear tabla (si quieres tipos correctos, ajusta aquí)
    c.execute("DROP TABLE IF EXISTS clientes")
    cols_def = []
    for s in slots:
        if s['name'] in ['precio_vivienda', 'entrada', 'importe_a_financiar', 'gastos_mensuales_est', 'ingresos_netos_mensuales', 'plazo_anos', 'tasa_interes_anual',
                         'ingresos_netos_mensuales', 'gastos_mensuales_est', 'aportaciones_adicionales']:
            tipo = "REAL"
        elif s['name'] in ['avalista', 'cliente_es_cliente_banco', 'consentimiento_ficheros',
                           'consentimiento_tratamiento_datos']:
            tipo = "INTEGER"  # 0/1 para booleanos
        else:
            tipo = "TEXT"
        cols_def.append(f"{s['name']} {tipo}")
    c.execute(f"CREATE TABLE IF NOT EXISTS clientes ({', '.join(cols_def)})")

    # Iterar sobre slots
    for slot in slots:
        while True:
            print("Agente:", slot["prompt"])
            user_input = input("Usuario: ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("Agente: ¡Hasta pronto!")
                conn.close()
                return

            # Validar/limpiar respuesta con LLM
            valor_limpio = validar_con_modelo(slot, user_input)
            if valor_limpio is None:
                print(f"Agente: No entendí tu respuesta para {slot['name']}, inténtalo de nuevo.")
                continue

            form_data[slot["name"]] = valor_limpio
            prompts.append({"role": "user", "content": f"{slot['name']}: {valor_limpio}"})
            break

    # Guardar en SQLite
    cols_str = ", ".join(form_data.keys())
    placeholders = ", ".join(["?"] * len(form_data))
    # Convertir booleanos a 0/1
    valores = [1 if v is True else 0 if v is False else v for v in form_data.values()]
    c.execute(f"INSERT INTO clientes ({cols_str}) VALUES ({placeholders})", tuple(valores))
    conn.commit()
    conn.close()
    print("\nDatos guardados correctamente en la base de datos.")
