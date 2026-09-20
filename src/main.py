import cargar_datos
import analisis_proyecto
import eda_proyecto
import analisis_chatbot


def main():
    print("SISTEMA DE ANALISIS - BIBLIOTECA ACADEMICA")

    print("\n>>> 1. Resumen general de los datos")
    cargar_datos.main()

    print("\n>>> 2. Estadisticas del proyecto")
    analisis_proyecto.main()

    print("\n>>> 3. Analisis exploratorio (NumPy y Matplotlib)")
    eda_proyecto.main()

    print("\n>>> 4. Analisis para el chatbot (disponibilidad y ubicacion)")
    analisis_chatbot.main()


if __name__ == "__main__":
    main()
