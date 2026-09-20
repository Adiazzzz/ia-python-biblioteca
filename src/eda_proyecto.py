import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # Genera imágenes sin necesitar pantalla (necesario en Docker)
import matplotlib.pyplot as plt
import numpy as np

from cargar_datos import cargar_todo

CARPETA_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "graficos")


def construir_stock_prestamos(libros, ejemplares, prestamos_ejemplar):
    """
    Cruza libro.csv, ejemplar.csv y prestamo_ejemplar.csv.
    Retorna una lista de diccionarios: {id_libro, titulo, stock, prestamos}.
    """
    ejemplar_a_libro = {e["id_ejemplar"]: e["id_libro"] for e in ejemplares}

    conteo = Counter()
    for pe in prestamos_ejemplar:
        id_libro = ejemplar_a_libro.get(pe["id_ejemplar"])
        if id_libro is not None:
            conteo[id_libro] += 1

    resultado = []
    for libro in libros:
        resultado.append({
            "id_libro": libro["id_libro"],
            "titulo": libro["titulo"],
            "stock": int(libro["stock"]),
            "prestamos": conteo.get(libro["id_libro"], 0),
        })
    return resultado


def estadisticas_numpy(valores):
    """Calcula promedio, máximo, mínimo y desviación estándar con NumPy."""
    arreglo = np.array(valores, dtype=float)
    return {
        "promedio": float(np.mean(arreglo)),
        "maximo": float(np.max(arreglo)),
        "minimo": float(np.min(arreglo)),
        "desviacion": float(np.std(arreglo)),
    }


def libros_alta_demanda_bajo_stock(tabla, min_prestamos=3, max_stock=3):
    """Libros con muchos préstamos y pocos ejemplares (candidatos a comprar más)."""
    stock = np.array([f["stock"] for f in tabla])
    prestamos = np.array([f["prestamos"] for f in tabla])
    indices = np.where((prestamos >= min_prestamos) & (stock <= max_stock))[0]
    candidatos = [tabla[i] for i in indices]
    return sorted(candidatos, key=lambda f: f["prestamos"], reverse=True)


def grafico_distribucion(tabla):
    prestamos = np.array([f["prestamos"] for f in tabla])
    plt.figure(figsize=(8, 5))
    plt.hist(prestamos, bins=range(0, int(prestamos.max()) + 2),
             color="orange", edgecolor="black", align="left")
    plt.title("Distribución de préstamos por libro")
    plt.xlabel("Cantidad de préstamos")
    plt.ylabel("Cantidad de libros")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CARPETA_SALIDA, "distribucion_prestamos.png"), dpi=150)
    plt.close()


def grafico_stock_vs_prestamos(tabla):
    stock = np.array([f["stock"] for f in tabla])
    prestamos = np.array([f["prestamos"] for f in tabla])
    niveles = sorted(set(stock.tolist()))
    promedios = [float(np.mean(prestamos[stock == n])) for n in niveles]

    plt.figure(figsize=(8, 5))
    barras = plt.bar([str(n) for n in niveles], promedios, color="seagreen", edgecolor="black")
    plt.bar_label(barras, fmt="%.2f")
    plt.title("Promedio de préstamos según el stock del libro")
    plt.xlabel("Stock (ejemplares por libro)")
    plt.ylabel("Promedio de préstamos por libro")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CARPETA_SALIDA, "stock_vs_prestamos.png"), dpi=150)
    plt.close()
    return dict(zip(niveles, promedios))


def main():
    datos = cargar_todo()
    tabla = construir_stock_prestamos(datos["libro"], datos["ejemplar"], datos["prestamo_ejemplar"])
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    print("ANÁLISIS EXPLORATORIO (EDA) - BIBLIOTECA COTECNOVA")
    print(f"Libros analizados: {len(tabla)}")
    for variable in ["stock", "prestamos"]:
        est = estadisticas_numpy([f[variable] for f in tabla])
        print(f"\n{variable.upper()}")
        for nombre, valor in est.items():
            print(f"  {nombre}: {valor:.2f}")

    sin_prestamos = sum(1 for f in tabla if f["prestamos"] == 0)
    print(f"\nHallazgo 1: {sin_prestamos} de {len(tabla)} libros nunca se han prestado "
          f"({sin_prestamos / len(tabla) * 100:.1f}%).")

    promedios = grafico_stock_vs_prestamos(tabla)
    print("Hallazgo 2: promedio de préstamos por nivel de stock:")
    for nivel, prom in promedios.items():
        print(f"  stock {nivel}: {prom:.2f}")
    correlacion = np.corrcoef([f["stock"] for f in tabla], [f["prestamos"] for f in tabla])[0, 1]
    print(f"  Correlación stock-préstamos: {correlacion:.2f} "
          "(a más ejemplares, más préstamos en total)")

    grafico_distribucion(tabla)
    candidatos = libros_alta_demanda_bajo_stock(tabla)
    print(f"\nLibros con 3+ préstamos y stock <= 3: {len(candidatos)}")
    for f in candidatos[:5]:
        print(f"  - {f['titulo']} | stock {f['stock']} | préstamos {f['prestamos']}")
    print(f"\nGráficos guardados en: {os.path.abspath(CARPETA_SALIDA)}")


if __name__ == "__main__":
    main()