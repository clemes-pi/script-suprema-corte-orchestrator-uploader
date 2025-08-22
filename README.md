# script-suprema-corte-orchestrator-uploader

# court-docs-processor (Orchestrator batch uploader)

Script en Python para **subir en lote** documentos legales (`.docx`, `.pdf`, `.txt`) a un endpoint HTTP
(`POST /v1/process`) como **multipart/form-data** (campo `file`). Recorre recursivamente subcarpetas y
guarda la respuesta JSON por archivo, manteniendo una estructura de salida ordenada.

## Requisitos
- Python 3.11+
- `pip install requests`

## Instalación
```bash
# Clonar el repo (o crear carpeta y copiar los .py)
git clone https://github.com/<tu-usuario>/court-docs-processor.git
cd court-docs-processor

# Instalar dependencias
pip install -r requirements.txt  # si usás requirements.txt
# ó directamente:
pip install requests
