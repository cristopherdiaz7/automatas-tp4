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

def top_10_de_artista(df):
    artista_input = input("🎤 Ingresá el nombre del artista: ").strip()

    filtro = df[df["Artist"].str.contains(artista_input, case=False, na=False)]

    if filtro.empty:
        print("No se encontraron canciones para ese artista.")
        return

    col_reproducciones = "Streams" if "Streams" in filtro.columns else "Views"
    filtro = filtro.sort_values(by=col_reproducciones, ascending=False)

    top_10 = filtro.head(10)

    print(f"\n🎧 Top 10 canciones de {artista_input.title()}:")
    for _, fila in top_10.iterrows():
        artista = fila["Artist"]
        cancion = fila["Track"]
        duracion_ms = int(fila["Duration_ms"])
        duracion = pd.to_timedelta(duracion_ms, unit='ms')
        tiempo = str(duracion).split(".")[0]
        reproducciones = int(fila[col_reproducciones]) / 1_000_000
        print(f"{artista} - {cancion} | {tiempo} | {reproducciones:.2f}M reproducciones")

def insertar_registro_manual(df):
    print("\n✍️ Insertar nuevo registro manualmente:")

    artist = input("Artista: ").strip()
    track = input("Título del tema: ").strip()
    album = input("Álbum: ").strip()

    uri_spotify = input("URI de Spotify: ").strip()
    url_spotify = input("URL de Spotify: ").strip()
    url_youtube = input("URL de YouTube: ").strip()

    duracion_input = input("Duración (HH:MM:SS): ").strip()
    patron_duracion = re.compile(r"^\d{2}:\d{2}:\d{2}$")
    if not patron_duracion.match(duracion_input):
        print("Formato de duración inválido. Debe ser HH:MM:SS.")
        return
    h, m, s = map(int, duracion_input.split(":"))
    duracion_ms = ((h * 60 + m) * 60 + s) * 1000

    patron_url = re.compile(r"^https?://\S+$")
    if not patron_url.match(url_spotify) or not patron_url.match(url_youtube):
        print("Alguna URL no tiene formato válido.")
        return

    try:
        likes = int(input("Likes: "))
        views = int(input("Views: "))
    except ValueError:
        print("Likes y Views deben ser números enteros.")
        return

    if likes > views:
        print("No puede haber más likes que vistas.")
        return


    nuevo_registro = {
        "Artist": artist,
        "Track": track,
        "Album": album,
        "Uri": uri_spotify,
        "Duration_ms": duracion_ms,
        "URL_spotify": url_spotify,
        "URL_youtube": url_youtube,
        "Likes": likes,
        "Views": views
    }

    df.loc[len(df)] = nuevo_registro
    print("✅ Registro insertado correctamente.")


def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccioná una opción: ")

        if opcion == "1":
            buscar_titulo_o_artista(df)
        elif opcion == "2":
            top_10_de_artista(df)
        elif opcion == "3":
            insertar_registro_manual(df)
        elif opcion == "4":
            print("Mostrar álbumes (a implementar)")
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intentá de nuevo.")


if __name__ == "__main__":
    main()