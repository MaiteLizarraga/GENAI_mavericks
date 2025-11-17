# schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
import re

# --- Slot: cliente_es_cliente_banco ---
class ClienteBancoSlot(BaseModel):
    cliente_es_cliente_banco: bool

    @field_validator("cliente_es_cliente_banco", mode="before")
    def validar_si_no(cls, v):
        """Convierte respuestas tipo 'sí/no' a booleano"""
        if isinstance(v, bool):
            return v
        if not isinstance(v, str):
            raise ValueError("Se esperaba 'sí' o 'no'")
        v_lower = v.strip().lower()
        if v_lower in ["sí", "si", "s", "yes"]:
            return True
        elif v_lower in ["no", "n"]:
            return False
        else:
            raise ValueError("La respuesta debe ser 'sí' o 'no'")


# --- Slot: nombre_completo ---
class NombreCompletoSlot(BaseModel):
    nombre_completo: str

    @field_validator("nombre_completo")
    def nombre_no_vacio(cls, v):
        if not v.strip() or len(v.strip()) < 3:
            raise ValueError("El nombre completo no puede estar vacío ni tener menos de 3 caracteres")
        return v


# --- Slot: dni_nie ---
class DniNieSlot(BaseModel):
    dni_nie: str

    @field_validator("dni_nie")
    def validar_dni_nie(cls, v):
        pattern_dni = r'^\d{8}[A-Za-z]$'
        pattern_nie = r'^[XYZ]\d{7}[A-Za-z]$'
        if not (re.match(pattern_dni, v) or re.match(pattern_nie, v)):
            raise ValueError("DNI/NIE inválido")
        return v.upper()


# --- Slot: fecha_nacimiento ---
class FechaNacimientoSlot(BaseModel):
    fecha_nacimiento: str  # DD/MM/YYYY

    @field_validator("fecha_nacimiento")
    def validar_edad_adulto(cls, v):
        try:
            fecha = datetime.strptime(v, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Formato de fecha debe ser DD/MM/YYYY")
        hoy = date.today()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad < 18:
            raise ValueError("Debe ser mayor de 18 años")
        return v


# --- Slot: direccion_postal ---
class DireccionPostalSlot(BaseModel):
    direccion_postal: str

    @field_validator("direccion_postal")
    def direccion_valida(cls, v):
        if not v.strip() or len(v.strip()) < 10:
            raise ValueError("La dirección postal es demasiado corta")
        return v


# --- Slot: telefono ---
class TelefonoSlot(BaseModel):
    telefono: str

    @field_validator("telefono")
    def validar_telefono(cls, v):
        telefono_pat = r'^\+?\d{9,15}$'
        if not re.match(telefono_pat, v.strip()):
            raise ValueError("Teléfono inválido")
        return v.strip()


# --- Slot: email ---
class EmailSlot(BaseModel):
    email: str

    @field_validator("email")
    def validar_email(cls, v):
        email_pat = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_pat, v.strip()):
            raise ValueError("Email inválido")
        return v.strip()


# --- Slot: tipo_vivienda ---
class TipoViviendaSlot(BaseModel):
    tipo_vivienda: str

    @field_validator("tipo_vivienda")
    def tipo_vivienda_valida(cls, v):
        if v not in ["nueva", "segunda_mano"]:
            raise ValueError("Tipo de vivienda debe ser 'nueva' o 'segunda_mano'")
        return v


# --- Slot: precio_vivienda, entrada, importe_a_financiar, ingresos, gastos ---
class NumerosSlot(BaseModel):
    precio_vivienda: Optional[float] = Field(None, ge=0)
    entrada: Optional[float] = Field(None, ge=0)
    importe_a_financiar: Optional[float] = None
    ingresos_netos_mensuales: Optional[float] = None
    gastos_mensuales_est: Optional[float] = None

    @field_validator("precio_vivienda", "entrada", "importe_a_financiar",
                     "ingresos_netos_mensuales", "gastos_mensuales_est")
    def numeros_positivos(cls, v, info):
        if v is not None and v < 0:
            raise ValueError(f"{info.field_name} debe ser un número positivo")
        return v

    @field_validator("importe_a_financiar", mode="after")
    def calcular_importe_financiar(cls, v, info):
        """Si no se proporciona, se calcula automáticamente: precio - entrada"""
        data = info.data
        if v is None and data.get("precio_vivienda") is not None and data.get("entrada") is not None:
            return data["precio_vivienda"] - data["entrada"]
        return v
