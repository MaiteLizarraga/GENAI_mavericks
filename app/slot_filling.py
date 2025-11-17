import sqlite3
from validations import validar_con_modelo
from slot_loader import cargar_slots

def iniciar_slot_filling_json(prompts):
    slots, _ = cargar_slots()
    form_data = {}

    # Conectar SQLite
    conn = sqlite3.connect("clientes.db")
    c = conn.cursor()
    cols = ", ".join([f"{s['name']} TEXT" for s in slots])
    c.execute(f"CREATE TABLE IF NOT EXISTS clientes ({cols})")

    # Iterar sobre slots
    for slot in slots:
        while True:
            print("Agente:", slot["prompt"])
            user_input = input("Usuario: ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("Agente: ¡Hasta pronto!")
                conn.close()
                return

            # --- Extraer / limpiar respuesta con LLM ---
            valor_limpio = validar_con_modelo(slot, user_input)
            if valor_limpio is None:
                print(f"Agente: No entendí tu respuesta para {slot['name']}, inténtalo de nuevo.")
                continue

            # --- Guardar dato y prompt ---
            form_data[slot["name"]] = valor_limpio
            prompts.append({"role": "user", "content": f"{slot['name']}: {valor_limpio}"})
            break  # pasa al siguiente slot solo si fue válido

    # Guardar en SQLite
    cols_str = ", ".join(form_data.keys())
    placeholders = ", ".join(["?"] * len(form_data))
    c.execute(f"INSERT INTO clientes ({cols_str}) VALUES ({placeholders})", tuple(form_data.values()))
    conn.commit()
    conn.close()
    print("\n📄 Datos guardados correctamente en la base de datos.")