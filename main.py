import pandas as pd


try:
    df = pd.read_csv("data/spotify_and_youtube.csv")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo CSV. Asegurate de que esté en la carpeta 'data'.")
    exit()


def mostrar_menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Buscar por título o artista")
    print("2. Mostrar top 10 de un artista")
    print("3. Insertar un nuevo registro")
    print("4. Mostrar álbumes de un artista")
    print("5. Salir")


def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccioná una opción: ")

        if opcion == "1":
            print("Buscar por título o artista (a implementar)")
        elif opcion == "2":
            print("Top 10 de un artista (a implementar)")
        elif opcion == "3":
            print("Insertar registro (a implementar)")
        elif opcion == "4":
            print("Mostrar álbumes (a implementar)")
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intentá de nuevo.")


if __name__ == "__main__":
    main()
