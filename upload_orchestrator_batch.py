#!/usr/bin/env python3
# batch_orchestrator_recursive.py
import os, json, time, pathlib, mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# ===== Config =====
BASE_URL = os.getenv("ORCH_URL", "https://wac-escritosjudiciales-eastus-cac7gad8b5d0ebew.eastus-01.azurewebsites.net")
ENDPOINT = "/v1/process"
ACCEPT = "application/json"
IN_DIR = pathlib.Path(os.getenv("IN_DIR", "."))      # carpeta raíz a procesar (se pasa por argv también)
OUT_DIR = pathlib.Path(os.getenv("OUT_DIR", "responses"))
ALLOWED_EXT = {".docx", ".pdf", ".txt"}
MAX_WORKERS = int(os.getenv("WORKERS", "4"))         # subidas en paralelo
TIMEOUT = 120                                        # seg
MAX_RETRIES = 3

def iter_files_recursive(root: pathlib.Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT:
            yield p

def post_file(path: pathlib.Path):
    url = BASE_URL.rstrip("/") + ENDPOINT
    mime, _ = mimetypes.guess_type(str(path))
    files = {"file": (path.name, open(path, "rb"), mime or "application/octet-stream")}
    headers = {"accept": ACCEPT}
    try:
        r = requests.post(url, headers=headers, files=files, timeout=TIMEOUT)
        try:
            data = r.json()
        except Exception:
            data = None
        return r.status_code, data, r.text
    finally:
        files["file"][1].close()

def ensure_parent(path: pathlib.Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def upload_with_retries(fpath: pathlib.Path, rel: pathlib.Path):

    for attempt in range(1, MAX_RETRIES+1):
        try:
            status, js, txt = post_file(fpath)
            out_base = OUT_DIR / rel.with_suffix("")
            if status == 200:
                out_path = out_base.with_suffix(".response.json")
                ensure_parent(out_path)
                with open(out_path, "w", encoding="utf-8") as fh:
                    json.dump(js, fh, ensure_ascii=False, indent=2)
                return fpath, status, str(out_path)
            else:
                out_path = out_base.with_suffix(".error.json")
                ensure_parent(out_path)
                payload = {"status": status, "json": js, "text": txt[:2000]}
                with open(out_path, "w", encoding="utf-8") as fh:
                    json.dump(payload, fh, ensure_ascii=False, indent=2)
                return fpath, status, str(out_path)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == MAX_RETRIES:
                out_path = (OUT_DIR / rel.with_suffix("")).with_suffix(".error.json")
                ensure_parent(out_path)
                with open(out_path, "w", encoding="utf-8") as fh:
                    json.dump({"status": "network_error", "error": str(e)}, fh, ensure_ascii=False, indent=2)
                return fpath, "network_error", str(out_path)
            time.sleep(2 ** attempt)

def main():
    import sys
    if len(sys.argv) < 2:
        print("Uso: python batch_orchestrator_recursive.py <carpeta_raiz_con_subcarpetas>")
        sys.exit(1)

    root = pathlib.Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"No existe carpeta: {root}")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = list(iter_files_recursive(root))
    if not files:
        print("No se encontraron archivos .docx/.pdf/.txt.")
        sys.exit(0)

    print(f"Subiendo {len(files)} archivo(s) desde {root} → {BASE_URL}{ENDPOINT}")
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {}
        for f in files:
            rel = f.relative_to(root)  # conserva '/archivo.docx'
            futures[ex.submit(upload_with_retries, f, rel)] = rel
        for fut in as_completed(futures):
            fpath, status, outp = fut.result()
            print(f" → {futures[fut]} [{status}] ⇒ {outp}")
            results.append((str(futures[fut]), status, outp))

    # resumen CSV 
    csv_path = OUT_DIR / "summary.csv"
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write("relative_path,status,output_file\n")
        for rel, st, outp in results:
            fh.write(f"\"{rel}\",{st},\"{outp}\"\n")
    print(f"\nListo. Resumen: {csv_path}")

if __name__ == "__main__":
    main()