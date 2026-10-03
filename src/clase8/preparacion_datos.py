"""
preparacion_datos.py
Script para cargar, limpiar y preparar un dataset de ventas
utilizando Pandas y visualizar con Seaborn.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Sin pantalla (Docker/WSL): los gráficos solo se guardan en archivo
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Configurar el estilo de Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Rutas calculadas desde la ubicación del script (src/clase8/), no desde
# la carpeta donde se ejecute: funciona igual en WSL, Docker o VSCode.
RAIZ = Path(__file__).resolve().parents[2]
RUTA_CSV = RAIZ / "data" / "clase8" / "ventas_tienda.csv"
CARPETA_SALIDA = RAIZ / "outputs"


def guardar_figura(nombre):
    """Ajusta el diseño, guarda la figura actual en outputs/ y la cierra."""
    plt.tight_layout()
    plt.savefig(CARPETA_SALIDA / nombre, dpi=150)
    plt.close()


def cargar_datos(archivo_csv):
    """Carga el archivo CSV y retorna un DataFrame."""
    try:
        df = pd.read_csv(archivo_csv)
        print(f"Datos cargados correctamente: {df.shape[0]} filas, {df.shape[1]} columnas.")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_csv}' no existe.")
        return None


def explorar_datos(df):
    """Muestra información general y estadísticas descriptivas."""
    print("\nPRIMERAS 5 FILAS:")
    print(df.head())
    print("\nINFORMACIÓN GENERAL:")
    df.info()  # info() ya imprime por sí solo; con print() mostraría un "None" extra
    print("\nESTADÍSTICAS DESCRIPTIVAS:")
    print(df.describe())
    print("\nVALORES NULOS POR COLUMNA:")
    print(df.isnull().sum())


def limpiar_datos(df):
    """Limpia el DataFrame: maneja nulos y crea columnas derivadas."""
    df_limpio = df.copy()

    # 1. Manejar valores nulos en 'cliente_edad' con la mediana
    mediana_edad = df_limpio['cliente_edad'].median()
    df_limpio['cliente_edad'] = df_limpio['cliente_edad'].fillna(mediana_edad)
    print(f"\nValores nulos en 'cliente_edad' imputados con la mediana: {mediana_edad}")

    # 2. Crear columna 'total_venta'
    df_limpio['total_venta'] = df_limpio['precio_unitario'] * df_limpio['cantidad']
    print("Columna 'total_venta' creada.")

    # 3. Convertir 'fecha' a datetime y derivar el día de la semana (0 = lunes)
    df_limpio['fecha'] = pd.to_datetime(df_limpio['fecha'])
    df_limpio['dia_semana'] = df_limpio['fecha'].dt.dayofweek
    print("Columna 'fecha' convertida a datetime y 'dia_semana' creada.")

    return df_limpio


def visualizar_datos(df):
    """Genera visualizaciones con Seaborn."""
    # 1. Distribución del total de ventas
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x='total_venta', bins=10, kde=True, color='skyblue')
    plt.title('Distribución del Total de Ventas')
    plt.xlabel('Total de Venta ($)')
    plt.ylabel('Frecuencia')
    guardar_figura('distribucion_ventas.png')

    # 2. Total de ventas por categoría
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='categoria', y='total_venta', hue='categoria',
                estimator="sum", errorbar=None, palette='viridis', legend=False)
    plt.title('Total de Ventas por Categoría')
    plt.xlabel('Categoría')
    plt.ylabel('Total de Ventas ($)')
    guardar_figura('ventas_por_categoria.png')

    # 3. Relación entre edad y total de venta
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='cliente_edad', y='total_venta', hue='categoria',
                    style='metodo_pago', s=100)
    plt.title('Relación: Edad del Cliente vs Total de Venta')
    plt.xlabel('Edad del Cliente')
    plt.ylabel('Total de Venta ($)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    guardar_figura('edad_vs_venta.png')

    print(f"\nGráficos guardados en '{CARPETA_SALIDA}'.")


def preparar_ml(df):
    """Prepara el DataFrame para Machine Learning: codificación y selección."""
    df_ml = df.copy()

    # 1. Codificación One-Hot para 'categoria' y 'metodo_pago' (como 0/1)
    df_ml = pd.get_dummies(df_ml, columns=['categoria', 'metodo_pago'],
                           prefix=['cat', 'pago'], dtype=int)
    print("\nCodificación One-Hot aplicada.")

    # 2. Eliminar columnas no numéricas irrelevantes para el modelo
    #    ('fecha' ya quedó representada por 'dia_semana')
    columnas_a_eliminar = ['id_venta', 'fecha', 'producto', 'ciudad']
    df_ml = df_ml.drop(columns=columnas_a_eliminar, errors='ignore')
    print("Columnas no numéricas eliminadas.")

    # 3. Mostrar las primeras filas del DataFrame listo para ML
    print("\nDATAFRAME LISTO PARA MACHINE LEARNING (primeras 5 filas):")
    print(df_ml.head())

    return df_ml


def main():
    """Función principal del programa."""
    print("=" * 60)
    print("PREPARACIÓN DE DATOS PARA MACHINE LEARNING - VENTAS")
    print("=" * 60)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

    # 1. Cargar datos
    df = cargar_datos(RUTA_CSV)
    if df is None:
        return

    # 2. Explorar datos
    explorar_datos(df)

    # 3. Limpiar datos
    df_limpio = limpiar_datos(df)

    # 4. Visualizar datos
    visualizar_datos(df_limpio)

    # 5. Preparar para Machine Learning
    df_ml = preparar_ml(df_limpio)

    # 6. Guardar el DataFrame preparado
    ruta_salida = CARPETA_SALIDA / 'ventas_preparadas_ml.csv'
    df_ml.to_csv(ruta_salida, index=False)
    print(f"\nDataset preparado guardado como '{ruta_salida}'")
    print("\nProceso completado exitosamente.")


if __name__ == "__main__":
    main()
