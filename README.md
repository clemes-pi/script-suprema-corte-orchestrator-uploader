# script-suprema-corte-orchestrator-uploader

Script en Python para **subir en lote** documentos legales (`.docx`, `.pdf`, `.txt`) a un endpoint HTTP
(`POST /v1/process`) como **multipart/form-data** (campo `file`). Recorre recursivamente subcarpetas y
guarda la respuesta JSON por archivo, manteniendo una estructura de salida ordenada.

## Requisitos
- Python 3.11+
- `pip install requests`

Configuración

El script lee variables de entorno (opcionales):
ORCH_URL (default): https://wac-escritosjudiciales-eastus-cac7gad8b5d0ebew.eastus-01.azurewebsites.net
OUT_DIR (default): responses
WORKERS (default): 4 (subidas en paralelo, versión recursiva)

Ejemplo:
$env:ORCH_URL="https://wac-escritosjudiciales-eastus-cac7gad8b5d0ebew.eastus-01.azurewebsites.net"
$env:OUT_DIR="responses"
$env:WORKERS="6"

Endpoints esperados
POST /v1/process con form-data → key file (tipo File).
Header recomendado: accept: application/json
Este endpoint no acepta JSON crudo con el contenido del documento. Si enviás JSON, devolverá 422 (campo file requerido).

## Instalación
```bash
# Clonar el repo (o crear carpeta y copiar los .py)
git clone https://github.com/<tu-usuario>/court-docs-processor.git
cd court-docs-processor

# Instalar dependencias
pip install -r requirements.txt  # si usás requirements.txt
# ó directamente:
pip install requests
