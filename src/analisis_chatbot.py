import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cargar_datos import cargar_todo

CARPETA_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")


def estado_actual_ejemplares(prestamos, prestamos_ejemplar):
    """
    Devuelve {id_ejemplar: estado} usando el préstamo MÁS RECIENTE de cada ejemplar.
    Un ejemplar sin préstamos no aparece en el resultado.
    """
    fecha_de = {p["id_prestamo"]: (p["fecha_prestamo"], int(p["id_prestamo"])) for p in prestamos}
    ultimo = {}
    for pe in prestamos_ejemplar:
        clave = fecha_de.get(pe["id_prestamo"])
        if clave is None:
            continue
        ej = pe["id_ejemplar"]
        if ej not in ultimo or clave > ultimo[ej][0]:
            ultimo[ej] = (clave, pe["estado"])
    return {ej: estado for ej, (clave, estado) in ultimo.items()}


def estado_de_cada_ejemplar(datos):
    """
    Retorna {id_ejemplar: estado}, donde estado es Disponible, Prestado, Perdido o Dañado.
    Un ejemplar sin préstamos o cuyo último préstamo fue devuelto está Disponible.
    """
    ultimo_estado = estado_actual_ejemplares(datos["prestamo"], datos["prestamo_ejemplar"])
    nombres = {"Devuelto": "Disponible", "Prestado": "Prestado", "Perdido": "Perdido", "Danado": "Dañado"}
    resultado = {}
    for e in datos["ejemplar"]:
        estado = ultimo_estado.get(e["id_ejemplar"], "Devuelto")
        resultado[e["id_ejemplar"]] = nombres.get(estado, estado)
    return resultado


def contar_estados(estados):
    """Cuenta cuántos ejemplares hay en cada estado."""
    conteo = Counter(estados.values())
    return {k: conteo.get(k, 0) for k in ["Disponible", "Prestado", "Perdido", "Dañado"]}


def libros_sin_disponibilidad(datos, estados):
    """Títulos de libros que hoy no tienen ningún ejemplar disponible."""
    disponibles = Counter()
    for e in datos["ejemplar"]:
        if estados[e["id_ejemplar"]] == "Disponible":
            disponibles[e["id_libro"]] += 1
    return [l["titulo"] for l in datos["libro"] if disponibles[l["id_libro"]] == 0]


def no_disponibles_por_zona(datos, estados):
    """Cuenta ejemplares NO disponibles (prestados, perdidos o dañados) por zona de la biblioteca."""
    zona_de = {u["id"]: u["descripcion"].split(" - ")[0] for u in datos["ubicacion"]}
    conteo = Counter()
    for e in datos["ejemplar"]:
        if estados[e["id_ejemplar"]] != "Disponible":
            conteo[zona_de.get(e["id_ubicacion"], "?")] += 1
    return dict(sorted(conteo.items()))


def top_libros_prestados(datos, n=10):
    """Los n libros con más préstamos: lista de (título, préstamos)."""
    ejemplar_a_libro = {e["id_ejemplar"]: e["id_libro"] for e in datos["ejemplar"]}
    titulo_de = {l["id_libro"]: l["titulo"] for l in datos["libro"]}
    conteo = Counter()
    for pe in datos["prestamo_ejemplar"]:
        conteo[ejemplar_a_libro[pe["id_ejemplar"]]] += 1
    return [(titulo_de[i], c) for i, c in conteo.most_common(n)]


def grafico_estados(conteo):
    nombres = list(conteo.keys())
    valores = list(conteo.values())
    colores = ["seagreen", "orange", "firebrick", "goldenrod"]
    plt.figure(figsize=(8, 5))
    barras = plt.bar(nombres, valores, color=colores, edgecolor="black")
    plt.bar_label(barras)
    plt.title("Estado actual de los ejemplares de la biblioteca")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de ejemplares")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CARPETA_SALIDA, "estado_ejemplares.png"), dpi=150)
    plt.close()


def grafico_zonas(por_zona):
    zonas = list(por_zona.keys())
    valores = list(por_zona.values())
    plt.figure(figsize=(8, 5))
    barras = plt.bar(zonas, valores, color="steelblue", edgecolor="black")
    plt.bar_label(barras)
    plt.title("Ejemplares no disponibles por zona de la biblioteca")
    plt.xlabel("Zona")
    plt.ylabel("Ejemplares prestados, perdidos o dañados")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CARPETA_SALIDA, "no_disponibles_por_zona.png"), dpi=150)
    plt.close()


def grafico_top_libros(top):
    titulos = [t if len(t) <= 40 else t[:37] + "..." for t, _ in top][::-1]
    valores = [c for _, c in top][::-1]
    plt.figure(figsize=(9, 5.5))
    barras = plt.barh(titulos, valores, color="mediumpurple", edgecolor="black")
    plt.bar_label(barras)
    plt.title("Los 10 libros más prestados")
    plt.xlabel("Cantidad de préstamos")
    plt.grid(True, axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CARPETA_SALIDA, "top_libros_prestados.png"), dpi=150)
    plt.close()


def main():
    datos = cargar_todo()
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    estados = estado_de_cada_ejemplar(datos)

    print("ANÁLISIS PARA EL CHATBOT - DISPONIBILIDAD Y UBICACIÓN")

    conteo = contar_estados(estados)
    total = sum(conteo.values())
    print(f"\nEstado de {total} ejemplares:")
    for estado, cantidad in conteo.items():
        print(f"  {estado}: {cantidad} ({cantidad / total * 100:.1f}%)")
    grafico_estados(conteo)

    sin_disp = libros_sin_disponibilidad(datos, estados)
    total_libros = len(datos["libro"])
    print(f"\nLibros sin ningún ejemplar disponible hoy: {len(sin_disp)} de {total_libros} "
          f"({len(sin_disp) / total_libros * 100:.1f}%)")

    por_zona = no_disponibles_por_zona(datos, estados)
    valores = np.array(list(por_zona.values()))
    print("\nEjemplares no disponibles por zona:")
    for zona, cantidad in por_zona.items():
        print(f"  {zona}: {cantidad}")
    print(f"  Promedio por zona: {np.mean(valores):.1f} | máximo: {np.max(valores)} | "
          f"mínimo: {np.min(valores)} | desviación: {np.std(valores):.1f}")
    grafico_zonas(por_zona)

    top = top_libros_prestados(datos)
    print("\nLos 10 libros más prestados:")
    for titulo, cantidad in top:
        print(f"  - {titulo}: {cantidad} préstamos")
    grafico_top_libros(top)

    print(f"\nGráficos guardados en: {os.path.abspath(CARPETA_SALIDA)}")


if __name__ == "__main__":
    main()
