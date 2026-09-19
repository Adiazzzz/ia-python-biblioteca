
import csv
import os

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

ARCHIVOS_CSV = [
    "autor.csv",
    "autor_libro.csv",
    "editorial.csv",
    "ejemplar.csv",
    "genero.csv",
    "libro.csv",
    "libro_genero.csv",
    "prestamo.csv",
    "prestamo_ejemplar.csv",
    "ubicacion.csv",
    "usuario.csv",
]


def leer_datos(nombre_archivo):
    """Lee un CSV de la carpeta data/ y lo retorna como lista de diccionarios."""
    ruta = os.path.join(CARPETA_DATOS, nombre_archivo)
    datos = []
    try:
        with open(ruta, "r", encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                datos.append(fila)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {nombre_archivo}. Verifique la carpeta data/.")
    return datos


def cargar_todo():
    """Carga todos los CSV. Retorna {nombre_sin_extension: lista de diccionarios}."""
    datos = {}
    for nombre in ARCHIVOS_CSV:
        datos[nombre.replace(".csv", "")] = leer_datos(nombre)
    return datos


def mostrar_resumen(datos):
    """Imprime cuántos registros y qué columnas tiene cada tabla."""
    print("RESUMEN DE DATOS - BIBLIOTECA COTECNOVA")
    for nombre, filas in datos.items():
        columnas = list(filas[0].keys()) if filas else []
        print(f"\n{nombre}.csv -> {len(filas)} registros, {len(columnas)} columnas")
        print(f"  Columnas: {', '.join(columnas)}")


if __name__ == "__main__":
    mostrar_resumen(cargar_todo())
