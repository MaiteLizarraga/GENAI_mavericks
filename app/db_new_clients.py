import sqlite3
import datetime

# --- Inicialización de la base de datos ---
def init_db(db_path="hipotecas.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT,
            dni_nie TEXT,
            fecha_nacimiento TEXT,
            telefono TEXT,
            email TEXT,
            precio_vivienda REAL,
            entrada REAL,
            importe_a_financiar REAL,
            ingresos_netos_mensuales REAL,
            gastos_mensuales_est REAL,
            plazo_anos INTEGER,
            tasa_interes_anual REAL,
            cliente_es_cliente_banco BOOLEAN,
            consentimiento_tratamiento_datos BOOLEAN,
            consentimiento_ficheros BOOLEAN,
            fecha_registro TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Guardar los datos de un cliente ---
def guardar_cliente(datos, db_path="hipotecas.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Agregar fecha de registro
    datos["fecha_registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    columnas = ", ".join(datos.keys())
    placeholders = ", ".join(["?"] * len(datos))
    valores = list(datos.values())
    
    cursor.execute(f"INSERT INTO clientes ({columnas}) VALUES ({placeholders})", valores)
    conn.commit()
    conn.close()

def crear_registro_vacio(db_path="hipotecas.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (fecha_registro)
        VALUES (datetime('now'))
    """)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def actualizar_campo(cliente_id, campo, valor, db_path="hipotecas.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE clientes
        SET {campo} = ?
        WHERE id = ?
    """, (valor, cliente_id))
    conn.commit()
    conn.close()
