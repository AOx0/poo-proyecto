import pathlib
import random

import names

import pandas as pd
import matplotlib.pyplot as plt

random.seed(250)


def try_int(msg):
    try:
        return int(input(msg))
    except ValueError:
        print("Error: Ingrese una valor válido!")


def crear_registro(nombre_piloto):
    with open(nombre_piloto + ".csv", 'x+') as k:
        k.write("Posición,Velocidad Media,Velocidad Max")
        k.close()

        return pd.read_csv(nombre_piloto + ".csv")


def generar_posiciones(n_carreras, n_pilotos):
    posiciones_cada_carrera = []
    for _ in range(n_carreras):
        posiciones = [num + 1 for num in range(n_pilotos)]
        random.shuffle(posiciones)
        posiciones_cada_carrera.append(posiciones)

    return posiciones_cada_carrera


def generar_velocidades(n_carreras, n_pilotos):
    velocidades_cada_carrera = []
    for _ in range(n_carreras):
        velocidades_de_carrera = [random.randrange(150, 250) for _ in range(n_pilotos)]
        velocidades_de_carrera.sort()
        velocidades_cada_carrera.append(velocidades_de_carrera)

    return velocidades_cada_carrera


def cargar_piloto(nombre_piloto):
    return pd.read_csv(nombre_piloto + ".csv", index_col=0)


def guardar_piloto(df_pilot_a_guardar: pd.DataFrame, nombre):
    df_pilot_a_guardar.to_csv(nombre + ".csv")


def pedir_piloto(msg, df_):
    while True:
        nombre_piloto = input(msg)

        if nombre_piloto == "terminar":
            return "terminar"

        if nombre_piloto.isdecimal():
            print("Detectado índice de piloto")
            try:
                _ = df_.loc[int(nombre_piloto)].empty
                nombre_piloto = df_.loc[int(nombre_piloto)]["Piloto"]
                break
            except:
                print("Error: Ingrese un índice válido")
                continue

        if df_.loc[df_['Piloto'] == nombre_piloto].empty:
            print("Error: Ingrese un piloto válido")
        else:
            break

    return nombre_piloto


def pedir_stat(msg, df_):
    while True:
        try:
            nombre_stat = input(msg)

            if nombre_stat == "terminar":
                return "terminar"

            _ = df_[nombre_stat].to_list()
            return nombre_stat
        except:
            print("Ingresa el nombre de una estadística válida")


def main():
    file = input("Ingrese el nombre del archivo principal [default: datos.csv]: ")

    if file.replace("\n", "").replace(" ", "") == "":
        file = "datos.csv"

    if not pathlib.Path("datos.csv").exists():
        with open("datos.csv", "x+") as f:
            f.write("Piloto")

            f.close()

    df = pd.read_csv(file, index_col=0)
    primer_execution = df.empty

    if primer_execution:
        print("Warning: Primera ejecución del programa detectada!")

        carrera = try_int("Ingrese el número de carreras que va a registrar por piloto: ")

        num_pilotos = input("Ingrese el número de pilotos que desea generar aleatoriamente [default: rand]: ")

        if num_pilotos.isalnum():
            num_pilotos = int(num_pilotos)
        else:
            num_pilotos = random.randint(5, 20)

        posiciones_carreras = generar_posiciones(carrera, num_pilotos)
        velocidades_carreras = generar_velocidades(carrera, num_pilotos)
        for i in range(num_pilotos):

            nombre = names.get_full_name()
            print("Registrando datos para " + nombre)

            df_piloto = crear_registro(nombre)

            promedio_velocidad_carrera = 0
            promedio_position = 0
            for j in range(carrera):
                promedio_position += posiciones_carreras[j][i]
                promedio_velocidad_carrera += velocidades_carreras[j][posiciones_carreras[j][i] - 1]
                df_piloto = pd.concat([df_piloto, pd.DataFrame({
                    "Velocidad Media": [velocidades_carreras[j][posiciones_carreras[j][i] - 1]],
                    "Posición": [posiciones_carreras[j][i]],
                    "Velocidad Max": [velocidades_carreras[j][posiciones_carreras[j][i] - 1] + random.randrange(10, 25)]
                }, index=[j + 1])])

            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "Piloto": [nombre],
                            "Pos Promedio": promedio_position / carrera,
                            "Vel Promedio": promedio_velocidad_carrera / carrera
                        }, index=[i + 1])
                ]
            )

            df_piloto.to_csv(nombre + ".csv")
            df.to_csv("datos.csv")

    option = 0
    while option != 4:
        print(
            "Menu de opciones: \n"
            "    1. Consultar estadísticas\n"
            "    2. Agregar datos de nueva carrera\n"
            "    3. Eliminar todo\n"
            "    4. Salir\n"
        )

        option = try_int("Ingrese una opción: ")

        if option == 1:
            print(df)

            print("Selección de pilotos:\n"
                  "Ingrese el nombre de los pilotos que desee o 'terminar' para continuar")

            df_pilotos = {}
            while True:
                piloto = pedir_piloto("Ingrese el nombre o id del piloto: ", df)

                if piloto == "terminar":
                    break

                df_pilotos[piloto] = cargar_piloto(piloto)

            if not df_pilotos:
                continue

            for piloto in df_pilotos:
                print(piloto)
                print(df_pilotos[piloto])

            if input("Deseas graficar una estadística en específico: [si|no]: ").lower() == "si":
                print("Selección de stats:\n"
                      "Ingrese el nombre de las estadísticas que desee graficar o 'terminar' para continuar")

                df_stats = {}
                while True:
                    stat = pedir_stat("Ingrese una estadística a graficar: ", df_pilotos[list(df_pilotos.keys())[0]])

                    if stat == "terminar":
                        break

                    df_stats[stat] = True

                carreras = list(range(1, len(df_pilotos[list(df_pilotos.keys())[0]])+1))

                if not df_stats:
                    continue

                for stat in df_stats.keys():
                    fig, ax = plt.subplots()
                    for piloto in df_pilotos:
                        ax.plot(carreras, df_pilotos[piloto][stat].to_list(), label=piloto)

                    ax.set_title(stat, loc='center',
                                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
                    plt.legend()
                    plt.show()

        if option == 2:
            pilotos_cambiados = []
            posiciones_disponibles = [num + 1 for num in range(len(df))]

            aleatorio = input("Desea generar los datos de forma aleatoria [si|no]: ") == "si"

            posiciones_carreras = generar_posiciones(len(cargar_piloto(df["Piloto"][0])), len(df))
            velocidades_carreras = generar_velocidades(len(cargar_piloto(df["Piloto"][0])), len(df))

            # Se modifican todos los pilotos
            i = 0
            for piloto in df["Piloto"]:

                # Cargamos los datos del archivo de datos del piloto
                df_piloto = cargar_piloto(piloto)

                # Informamos al usuario qué corredor se está modificando
                print("Registrando datos para " + piloto)

                if not aleatorio:
                    # Nos aseguramos que la velocidad máxima sea válida
                    while True:
                        vel_max = try_int("Ingresa la velocidad máxima: ")
                        if not vel_max > 160:
                            print("La velocidad máxima debe ser mayor a 160")
                        else:
                            break

                    # Nos aseguramos que la velocidad media sea válida
                    while True:
                        vel_media = try_int("Ingresa la velocidad media: ")
                        if vel_media > vel_max:
                            print(
                                "La velocidad máxima (" + str(vel_max) + ") "
                                                                         "debe ser mayor a la velocidad media (" + str(
                                    vel_media) + ")"
                            )
                        else:
                            break

                    # Nos aseguramos que la posición sea válida y única
                    while True:
                        posicion = try_int("Ingresa la posición: ")
                        if posicion not in posiciones_disponibles:
                            print("La posicion ya fue registrada para otro corredor.")
                            print("Posiciones disponibles: " + str(posiciones_disponibles))
                        else:
                            break

                    df_piloto = pd.concat([df_piloto, pd.DataFrame({
                        "Velocidad Media": vel_media,
                        "Posición": posicion,
                        "Velocidad Max": vel_max
                    }, index=[len(df_piloto) + 1])])

                    # Reducimos el número de posiciones disponibles para los demás corredores
                    posiciones_disponibles.remove(posicion)
                else:
                    df_piloto = pd.concat([df_piloto, pd.DataFrame({
                        "Velocidad Media": [velocidades_carreras[0][posiciones_carreras[0][i] - 1]],
                        "Posición": [posiciones_carreras[0][i]],
                        "Velocidad Max": [
                            velocidades_carreras[0][posiciones_carreras[0][i] - 1] + random.randrange(10, 25)]
                    }, index=[len(df_piloto) + 1])])

                i += 1

                # Almacenamos el piloto modificado y su nuevo estado en un arreglo de pilotos listos
                pilotos_cambiados.append((df_piloto, piloto))

            # Nos aseguramos de que se terminen de registrar todos los nuevos datos.
            # Por lo tanto, almacenamos hasta el final
            for df_piloto, piloto in pilotos_cambiados:
                guardar_piloto(df_piloto, piloto)

        if option == 3:
            import os
            test = os.listdir(".")

            for item in test:
                if item.endswith(".csv"):
                    os.remove(os.path.join(".", item))

            print("Todos los datos han sido eliminados")
            print("Volviendo a ejecutar el programa...")
            main()


if __name__ == "__main__":
    main()
