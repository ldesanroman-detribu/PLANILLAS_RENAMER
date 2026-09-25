"""
Detecta celdas con error #VALUE! en todos los archivos .xlsx de una carpeta.
Uso: python detectar_value_errors.py "C:/ruta/a/tu/carpeta"
"""

import sys
import os
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def escanear_archivo(ruta):
    errores = []
    try:
        wb = load_workbook(ruta, data_only=True)
        for nombre_hoja in wb.sheetnames:
            hoja = wb[nombre_hoja]
            for fila in hoja.iter_rows():
                for celda in fila:
                    if celda.value == "#VALUE!":
                        col_letra = get_column_letter(celda.column)
                        errores.append({
                            "hoja": nombre_hoja,
                            "celda": f"{col_letra}{celda.row}",
                            "fila": celda.row,
                            "columna": col_letra,
                        })
    except Exception as e:
        return None, str(e)
    return errores, None


def escanear_carpeta(carpeta):
    carpeta = Path(carpeta)
    archivos = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls"))

    if not archivos:
        print(f"No se encontraron archivos Excel en: {carpeta}")
        return

    print(f"\nEscaneando {len(archivos)} archivo(s) en: {carpeta}\n")
    print("=" * 60)

    archivos_con_error = []

    for archivo in sorted(archivos):
        print(f"Revisando: {archivo.name} ...", end=" ")
        errores, excepcion = escanear_archivo(archivo)

        if excepcion:
            print(f"⚠️  No se pudo abrir ({excepcion})")
            continue

        if errores:
            print(f"❌ {len(errores)} error(es) encontrado(s)")
            archivos_con_error.append((archivo.name, errores))
            for e in errores:
                print(f"     → Hoja: '{e['hoja']}' | Celda: {e['celda']}")
        else:
            print("✅ Sin errores")

    print("\n" + "=" * 60)
    if archivos_con_error:
        print(f"\n⚠️  RESUMEN: {len(archivos_con_error)} archivo(s) con #VALUE!:\n")
        for nombre, errores in archivos_con_error:
            print(f"  • {nombre} ({len(errores)} celda(s) con error)")
    else:
        print("\n✅ Todos los archivos están limpios de #VALUE!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Si no se pasa argumento, escanea la carpeta actual
        carpeta = Path.cwd()
        print(f"No se indicó carpeta. Usando carpeta actual: {carpeta}")
    else:
        carpeta = Path(sys.argv[1])

    if not carpeta.exists():
        print(f"Error: La carpeta '{carpeta}' no existe.")
        sys.exit(1)

    escanear_carpeta(carpeta)