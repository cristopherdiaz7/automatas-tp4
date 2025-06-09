import pandas as pd
import re
import os

CSV_PATH = "spotify_and_youtube.csv"
COLUMNS_ORDER = [
    "Index", "Artist", "Url_spotify", "Track", "Album", "Album_type", "Uri",
    "Danceability", "Energy", "Key", "Loudness", "Speechiness", "Acousticness",
    "Instrumentalness", "Liveness", "Valence", "Tempo", "Duration_ms",
    "Url_youtube", "Title", "Channel", "Views", "Likes", "Comments",
    "Licensed", "official_video", "Stream"
]

try:
    df = pd.read_csv(CSV_PATH)
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
        print("❌ No se encontraron coincidencias.")
        return

    # Determinar la columna de reproducciones
    col_reproducciones = "Stream" if "Stream" in resultados.columns else "Views"
    resultados = resultados.copy()  # ⚠️ Evita SettingWithCopyWarning
    resultados[col_reproducciones] = pd.to_numeric(resultados[col_reproducciones], errors="coerce")

    # Ordenar
    resultados = resultados.sort_values(by=col_reproducciones, ascending=False)

    print("\n🎵 Resultados encontrados:")
    for _, fila in resultados.iterrows():
        artista = fila["Artist"]
        cancion = fila["Track"]
        try:
            duracion_ms = int(float(fila["Duration_ms"]))
            duracion = pd.to_timedelta(duracion_ms, unit='ms')
            tiempo = str(duracion).split(" ")[-1]
        except:
            tiempo = "duración desconocida"

        print(f"{artista} - {cancion} ({tiempo})")


def top_10_de_artista(df):
    artista_input = input("Ingresá el nombre del artista: ").strip()
    filtro = df[df["Artist"].str.contains(artista_input, case=False, na=False)]

    if filtro.empty:
        print("No se encontraron canciones para ese artista.")
        return

    col_reproducciones = "Stream" if "Stream" in filtro.columns else "Views"
    filtro = filtro.sort_values(by=col_reproducciones, ascending=False)
    top_10 = filtro.head(10)

    print(f"\n Top 10 canciones de {artista_input.title()}:")
    for _, fila in top_10.iterrows():
        artista = fila["Artist"]
        cancion = fila["Track"]
        duracion_ms = int(fila["Duration_ms"])
        duracion = pd.to_timedelta(duracion_ms, unit='ms')
        tiempo = str(duracion).split(".")[0]
        reproducciones = int(fila[col_reproducciones]) / 1_000_000
        print(f"{artista} - {cancion} | {tiempo} | {reproducciones:.2f}M reproducciones")

def insertar_registro(df):
    print("\n--- Inserción de registros ---")
    print("1. Ingresar registro manualmente")
    print("2. Importar registros desde archivo CSV")
    eleccion = input("Seleccioná una opción: ").strip()

    if eleccion == "1":
        df = insertar_registro_manual(df)
    elif eleccion == "2":
        df = insertar_registros_desde_csv(df)
    else:
        print("❌ Opción inválida.")
    return df

def insertar_registro_manual(df):
    print("\n✍ Insertar nuevo registro manualmente:")

    data = {}
    data["Artist"] = input("Artista: ").strip()
    data["Track"] = input("Título del tema: ").strip()
    data["Album"] = input("Álbum: ").strip()
    data["Album_type"] = input("Tipo de álbum (e.g. single, album): ").strip()
    data["Uri"] = input("URI de Spotify (obligatorio): ").strip()
    if not data["Uri"]:
        print("❌ URI es obligatoria.")
        return df

    url_spotify = input("URL de Spotify: ").strip()
    url_youtube = input("URL de YouTube: ").strip()
    patron_url = re.compile(r"^https?://(open\.spotify\.com|www\.youtube\.com|youtu\.be)/[\w\-?=&#./]+$")
    if not patron_url.match(url_spotify) or not patron_url.match(url_youtube):
        print("❌ Una o ambas URLs tienen formato inválido.")
        return df

    data["Url_spotify"] = url_spotify
    data["Url_youtube"] = url_youtube

    duracion_input = input("Duración (HH:MM:SS): ").strip()
    if not re.match(r"^\d{2}:\d{2}:\d{2}$", duracion_input):
        print("Formato de duración inválido. Debe ser HH:MM:SS.")
        return df
    h, m, s = map(int, duracion_input.split(":"))
    data["Duration_ms"] = ((h * 60 + m) * 60 + s) * 1000

    try:
        data["Likes"] = int(input("Likes: "))
        data["Views"] = int(input("Views: "))
        if data["Likes"] > data["Views"]:
            print("❌ No puede haber más likes que vistas.")
            return df
    except ValueError:
        print("❌ Likes y Views deben ser números enteros.")
        return df

    data["Index"] = len(df)

    nuevo_registro = {col: data.get(col, "") for col in COLUMNS_ORDER}
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df = df[COLUMNS_ORDER]
    df.to_csv(CSV_PATH, index=False)
    print("✅ Registro insertado y guardado correctamente.")
    return df

def insertar_registros_desde_csv(df):
    path_csv_import = input("🗂 Ingresá la ruta del archivo CSV a importar: ").strip()
    if not os.path.exists(path_csv_import):
        print("❌ No se encontró el archivo.")
        return df
    try:
        nuevo_df = pd.read_csv(path_csv_import)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return df

    columnas_minimas = {"Artist", "Track", "Album", "Uri", "Duration_ms", "Url_spotify", "Url_youtube", "Likes", "Views"}
    if not columnas_minimas.issubset(nuevo_df.columns):
        faltantes = columnas_minimas - set(nuevo_df.columns)
        print(f"❌ El archivo no contiene las columnas mínimas requeridas: {faltantes}")
        return df

    for col in COLUMNS_ORDER:
        if col not in nuevo_df.columns:
            nuevo_df[col] = ""

    registros_validos = []

    for _, fila in nuevo_df.iterrows():
        try:
            # Validar duración
            if "Duration" in fila and pd.notna(fila["Duration"]):
                duracion = str(fila["Duration"])
                if not re.match(r"^\d{2}:\d{2}:\d{2}$", duracion):
                    raise ValueError("Duración inválida")
                h, m, s = map(int, duracion.split(":"))
                duracion_ms = ((h * 60 + m) * 60 + s) * 1000
            elif "Duration_ms" in fila:
                valor_duracion = fila["Duration_ms"]
                if pd.isna(valor_duracion) or str(valor_duracion).strip() == "":
                    raise ValueError("Duration_ms vacío o inválido")
                duracion_ms = int(float(valor_duracion))
            else:
                raise ValueError("Falta campo de duración")

            # Validar URLs
            url_spotify = str(fila.get("URL_spotify") or fila.get("Url_spotify", "")).strip()
            url_youtube = str(fila.get("URL_youtube") or fila.get("Url_youtube", "")).strip()
            if not re.match(r"^https?://\S+$", url_spotify):
                raise ValueError("URL Spotify inválida")
            if not re.match(r"^https?://\S+$", url_youtube):
                raise ValueError("URL YouTube inválida")

            # Validar números
            likes = int(fila["Likes"])
            views = int(fila["Views"])
            if likes > views:
                raise ValueError("Likes mayores que Views")

            fila["Duration_ms"] = duracion_ms
            fila["Url_spotify"] = url_spotify
            fila["Url_youtube"] = url_youtube

            registros_validos.append(fila)

        except Exception as e:
            print("❌ Registro inválido descartado.")

    if not registros_validos:
        print("⚠️ No se insertó ningún registro.")
        return df

    df_nuevos = pd.DataFrame(registros_validos)
    df_nuevos["Index"] = range(len(df), len(df) + len(df_nuevos))
    df_nuevos = df_nuevos[COLUMNS_ORDER]

    df = pd.concat([df, df_nuevos], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    print(f"✅ Se insertaron {len(df_nuevos)} registros correctamente.")
    return df



def mostrar_albumes_de_artista(df):
    artista_input = input("🎤 Ingresá el nombre del artista: ").strip()
    canciones = df[df["Artist"].str.contains(artista_input, case=False, na=False)]

    if canciones.empty:
        print(" No se encontraron canciones para ese artista.")
        return

    albums = canciones.groupby("Album")
    print(f"\n Álbumes de {artista_input.title()}:")
    print(f"Total de álbumes: {albums.ngroups}")

    for nombre_album, grupo in albums:
        cantidad_temas = len(grupo)
        duracion_total_ms = grupo["Duration_ms"].sum()
        duracion_total = pd.to_timedelta(duracion_total_ms, unit='ms')
        duracion_str = str(duracion_total).split(".")[0]

        print(f"\n Álbum: {nombre_album}")
        print(f" - Canciones: {cantidad_temas}")
        print(f" - Duración total: {duracion_str}")

def main():
    global df
    while True:
        mostrar_menu()
        opcion = input("Seleccioná una opción: ")

        if opcion == "1":
            buscar_titulo_o_artista(df)
        elif opcion == "2":
            top_10_de_artista(df)
        elif opcion == "3":
            df = insertar_registro(df)
        elif opcion == "4":
            mostrar_albumes_de_artista(df)
        elif opcion == "5":
            df.to_csv("data/spotify_and_youtube.csv", index=False)
            print("Cambios guardados en 'spotify_and_youtube.csv'.")
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intentá de nuevo.")

if __name__ == "__main__":
    main()


