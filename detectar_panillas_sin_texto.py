
import sys
import os
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def escanear_archivo(ruta, texto_buscado):
    """
    Returns (False, None) if the file DOES contain the string.
    Returns (True, None) if the file does NOT contain the string.
    Returns (None, error_msg) on failure.
    """
    try:
        wb = load_workbook(ruta, data_only=True)
        for nombre_hoja in wb.sheetnames:
            hoja = wb[nombre_hoja]
            for fila in hoja.iter_rows():
                for celda in fila:
                    if celda.value is not None and texto_buscado in str(celda.value):
                        return False, None  # Found it — file is NOT missing it
        return True, None  # Never found it — file IS missing the string
    except Exception as e:
        return None, str(e)


def encontrar_archivos_sin_texto(carpeta, texto_buscado):
    carpeta = Path(carpeta)
    rutas = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls"))
    archivos_sin_texto = []
    errores = {}
    total = len(rutas)

    for i, ruta in enumerate(rutas, start=1):
        print(f"[{i}/{total}] Escaneando: {ruta.name} ...", end=" ", flush=True)

        falta, error = escanear_archivo(ruta, texto_buscado)

        if error:
            errores[ruta] = error
            print("ERROR")
        elif falta:
            archivos_sin_texto.append(ruta)
            print("NO ENCONTRADO")
        else:
            print("OK")

    return archivos_sin_texto, errores



"""
Main
"""

if __name__ == "__main__":
    print("=== Detector de planillas sin texto ===\n")

    carpeta = input("Carpeta a escanear: ").strip().strip('"')
    texto_buscado = input("Texto a buscar: ").strip()

    carpeta = Path(carpeta)

    if not carpeta.exists():
        print(f"Error: La carpeta '{carpeta}' no existe.")
        sys.exit(1)

    if not carpeta.is_dir():
        print(f"Error: '{carpeta}' no es una carpeta.")
        sys.exit(1)

    rutas = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls"))

    if not rutas:
        print(f"No se encontraron archivos .xlsx/.xls en '{carpeta}'.")
        sys.exit(0)

    print(f"\nEscaneando {len(rutas)} archivos buscando: '{texto_buscado}'...\n")

    faltantes, errores = encontrar_archivos_sin_texto(carpeta, texto_buscado)

    print(f"\nArchivos que NO contienen '{texto_buscado}': {len(faltantes)}")
    for r in faltantes:
        print(f"  - {r.name}")

    if errores:
        print(f"\nErrores al leer ({len(errores)}):")
        for ruta, msg in errores.items():
            print(f"  - {ruta.name}: {msg}")