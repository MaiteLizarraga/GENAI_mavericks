# Guía para Probar el Orquestador

El proyecto incluye un archivo `requirements.txt` y una carpeta llamada `orquestador`.
Para clonar el repositorio utiliza:

```
git clone <URL_DEL_REPOSITORIO>
```

---

## 1. Crear y activar un entorno virtual
Crea el entorno en el directorio en el que este el repositorio clonado utilizando este comando:

```
python -m venv myvenv
```

Activar el entorno:

```
.\myvenv\Scripts\activate
```

---

## 2. Instalar dependencias

```
pip install -r requirements.txt
```

### Nota sobre PyTorch

Si aparece un error relacionado con PyTorch, puede deberse a la versión de Python que estás utilizando.

En el proyecto yo he utilizado Python 3.12.3.

Si es necesario, modifica la línea correspondiente en `requirements.txt`:

```
torch @ https://download.pytorch.org/whl/cpu/torch-2.5.1%2Bcpu-cp312-cp312-win_amd64.whl
```

Sustitúyela por la versión adecuada para tu entorno.

---

## 3. Ejecutar el orquestador

Accede a la carpeta:

```
cd orquestador
```

Ejecuta:

```
python graph_router.py
```

La carga inicial puede tardar un tiempo en lo que se carga el modelo por primera vez.

---

## 4. Permisos de micrófono

El programa utiliza reconocimiento de voz, por lo que deberás permitir el acceso al micrófono del equipo.

---

## 5. Uso del programa

Al iniciar aparecerá:

```
Ajustando ruido ambiente...
```

Espera hasta ver:

```
Habla ahora...
```

No hables antes de este mensaje.

Ejemplos de preguntas:

* "Cuál es la edad mínima para pedir una hipoteca"
* "A qué hora abre el banco los lunes"

El modelo definido en `model.py` clasificará tu consulta en categorías como "hipotecas" o "faq".

---

## 6. Finalizar el programa

Cuando aparezca:

```
Alguna otra pregunta? (enter para continuar, escribe 'no' para salir):
```

Escribe:

```
no
```

para finalizar la ejecución.
