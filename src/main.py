import cargar_datos
import analisis_chatbot


def main():
    print("SISTEMA DE ANALISIS - BIBLIOTECA COTECNOVA")

    print("\n>>> 1. Resumen general de los datos")
    datos = cargar_datos.cargar_todo()
    cargar_datos.mostrar_resumen(datos)

    print("\n>>> 2. Analisis para el chatbot (disponibilidad y ubicacion)")
    analisis_chatbot.main()


if __name__ == "__main__":
    main()