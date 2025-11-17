1. Crear un entorno virtual
python -m venv venv

2. Activar entorno
Windows (cmd)
.\venv\Scripts\activate.bat

PowerShell (VSC)
.\venv\Scripts\Activate.ps1

3. Instalar dependencias compiladas
pip-compile requirements.in
pip install -r requirements.txt

4. Verificar instalación
pip show langchain

5. Ejecutar script
python maite.py