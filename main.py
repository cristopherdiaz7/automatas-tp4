import pandas as pd
import re

try:
    df = pd.read_csv("data/spotify_and_youtube.csv")
except FileNotFoundError:
    print("No se encontró el archivo CSV. Asegurate de que esté en la carpeta 'data'.")
    exit()


def mostrar_menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Buscar por título o artista")
    print("2. Mostrar top 10 de un artista")
    print("3. Insertar un nuevo registro")
    print("4. Mostrar álbumes de un artista")
    print("5. Salir")


def buscar_titulo_o_artista(df):
    texto = input("Ingresá parte del título o artista: ").strip()

    patron = re.compile(re.escape(texto), re.IGNORECASE)

    resultados = df[df['Track'].apply(lambda x: bool(patron.search(str(x)))) |
                    df['Artist'].apply(lambda x: bool(patron.search(str(x))))]

    if resultados.empty:
        print("No se encontraron coincidencias.")
        return

    col_reproducciones = "Streams" if "Streams" in resultados.columns else "Views"
    resultados = resultados.sort_values(by=col_reproducciones, ascending=False)

    print("\n Resultados encontrados:")
    for _, fila in resultados.iterrows():
        artista = fila["Artist"]
        cancion = fila["Track"]
        duracion_ms = int(fila["Duration_ms"])
        duracion = pd.to_timedelta(duracion_ms, unit='ms')
        tiempo = str(duracion).split(" ")[-1]
        print(f"{artista} - {cancion} ({tiempo})")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccioná una opción: ")

        if opcion == "1":
            buscar_titulo_o_artista(df)
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