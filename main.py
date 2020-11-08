import jugadorm
from partida import Partida

'''
Intérprete del juego. Función principal que solicita comandos del jugador para reaccionar a la partida.
Puede recibir los comandos por línea de comandos o mediante un archivo.
'''


def interprete():
    print("Bienvenido a CENSURADO PARA DESCLASIFICACIÓN. Eres un Aniquilador "
          "del Imperio del hombre en una misión de purga de infiltrados")
    print("alienígenas en las profundidades de la ciudad colmena de Aevilles, Segmentum Solar.")
    print("En la refriega de la batalla, te has separado de tu escuadra y te enfrentas a la muerte.")
    print("¿Cuánto tiempo podrás sobrevivir?")
    print("------")

    # Solicitamos al usuario el modo (terminal o fichero) de ejecución
    modo = 0
    filename = ""
    file = None
    while modo < 1 or modo > 2:
        print("¿Qué modo desea emplear? Introduzca el número.\n1. Interactivo.\n2. Mediante fichero.")
        try:
            modo = int(input())
        except Exception as e:
            print("Modo no reconocido. Pruebe de nuevo.")

    # Si es modo fichero, solicitamos su nombre.
    if modo == 2:
        while file is None:
            try:
                print("Introduzca el nombre del archivo .txt de referencia")
                filename = input()
                file = open(filename)
            except Exception as e:
                print("Archivo no encontrado. Pruebe de nuevo.")
                file = None

    # Elección de clase
    print("Elige una clase de Aniquilador de las siguientes:")

    # Mostrar y guardar clases disponibles
    available_classes = []
    for clase in jugadorm.Aniquilador.__subclasses__():
        available_classes.append(clase.__name__)
        print(clase.getNombreClase())

    # Elegir clase
    class_selected = False
    while not class_selected:
        print("Introduce el nombre de una de ellas:")
        entrada_usuario = entrada(modo, file)
        try:
            # Somos permisivos con el formato de la clase
            class_selected = entrada_usuario.replace("á", "a").capitalize()
            if class_selected not in available_classes:
                class_selected = False
        except Exception as e:
            # print("Error: " + e)
            print('Clase no reconocida. Pruebe de nuevo.')

    # Elegir nombre y capítulo
    print("Escoge tu nombre:")
    nombre = entrada(modo, file)
    print("Algunos capítulos son CENSURADO PARA DESCLASIFICACIÓN...")
    print("Escoge un capítulo:")
    capitulo = entrada(modo, file)

    # Generamos el jugador (Aniquilador) a partir de tales datos
    jugador = eval("jugadorm.{}('{}','{}')".format(class_selected, nombre, capitulo))

    print("Eres {}, Aniquilador {} de los {}.".format(jugador.nombre, eval("jugadorm.{}.getNombreClase()"
                                                                            .format(class_selected)), jugador.capitulo))

    # Elegir armamento
    print("\n--- EQUIPAMIENTO ---")
    print("Armas cuerpo a cuerpo disponibles.")
    elegir_armamento(jugador, "cc", modo, file)
    print("\nArmas de disparo disponibles.")
    elegir_armamento(jugador, "dis", modo, file)

    print("\nEn cualquier momento, puedes ejecutar el comando 'ayuda' para recibir información sobre el juego.")
    print("Puedes salir del juego con el comando 'fin'.")
    print("")
    print("--- COMIENZA LA PARTIDA ---")

    # Creamos la partida. Movemos al jugador para que se cree una nueva sala.
    partida = Partida(jugador)
    partida.accion_jugador("mover")
    partida.comprobarEstado()

    while True:
        print("----")
        # Si el jugador muere (partida inactiva), acaba
        if not partida.activa:
            print("La partida ha finalizado.")
            break
        # Mostrar el estado actual del jugador
        jugador.estado_actual()

        # Mostrar acciones mediante introspección del jugador
        print("Acciones disponibles:")
        for accion in dir(jugador):
            if "accion_" in accion and callable(getattr(jugador, accion)):
                print(accion.replace("accion_", ""))

        print("Introduce una de tales acciones:")
        entrada_usuario = entrada(modo, file).lower()
        # Si es 'fin' se acaba.
        if entrada_usuario == "fin":
            print("Salir")
            break
        # Si es 'ayuda', menú de ayuda.
        elif entrada_usuario == "ayuda":
            ayuda(modo, file)
        # En cualquier otro caso...
        else:
            try:
                # Tratamos de ejecutarlo mediante generación de código
                partida.accion_jugador(entrada_usuario)
            # Si produce error, lo indicamos.
            except Exception as e:
                # print("Error: " + e)
                print('Comando no reconocido. Pruebe de nuevo.')
        partida.comprobarEstado()


'''
Muestra el armamento disponible del tipo indicado (cuerpo, distancia) y permite elegirlo al jugador.
'''


def elegir_armamento(jugador, tipo, modo, file):
    # Armas disponibles del tipo indicado
    armas_disponibles = (eval("jugador.armas_{}".format(tipo)))

    # Si no hay, se indica y no se toman más acciones.
    if len(armas_disponibles) == 0:
        print("Esta clase carece de armas de este tipo.")
    # Si sólo hay una, se equipa automáticamente y se muestra la información.
    elif len(armas_disponibles) == 1:
        print("Esta clase dispone de un único arma de este tipo. Se equipa automáticamente.")
        arma = armas_disponibles[0]
        print(str(arma))
        exec("jugador.elegir_arma_{}(0)".format(tipo))
        arma.efecto_pasivo()    # Se ejecuta el efecto pasivo del arma sobre el jugador.
    # Si hay 2+, se muestran las disponibles...
    else:
        for i in range(len(armas_disponibles)):
            print(str(armas_disponibles[i]))
            print("")

        # ... y se inicia un bucle en el que el jugador debe indicar el índice (válido) del arma a elegir.
        arma_selected = False
        while not arma_selected:
            try:
                print("Escoja una de las anteriores. Indique el número.")
                index = int(entrada(modo, file)) - 1
                if index >= 0:
                    exec("jugador.elegir_arma_{}(index)".format(tipo))
                    print("Se ha seleccionado {}.".format(armas_disponibles[index].nombre))
                    armas_disponibles[index].efecto_pasivo()
                    arma_selected = True
            except Exception as e:
                # print(e)
                print('Arma no reconocida. Pruebe de nuevo.')


'''
Menú de ayuda. Se muestran una serie de términos clave que, al introducirse, muestran la información requerida.
'''
def ayuda(modo, file):
    wiki = {
        "clases": "El jugador puede elegir tres clases:\nAsalto posee mayor fuerza vital "
                  "y se especializa en el cuerpo a cuerpo, pero carece de armamento a distancia."
                  "\nEl Capellán posee sendos tipos de arma, pero de estadísticas poco notables. No obstante, es"
                  " capaz de realizar litanías de batalla que otorgan efectos especiales."
                  "\nEl Táctico posee la mayor variedad de armas a distancia y las más efectivas.",
        "armas": "Existen dos tipos de armas: cuerpo a cuerpo y a distancia, que se emplean mediante las acciones"
                 "'golpear' y 'disparar', respectivamente.\n Las estadísticas muestran su nombre (Arma), impacto (I)"
                 ", herir (H), daño (D) y penetración (AP). Tales conceptos se explican en 'combate'.",
        "enemigos": "Los enemigos más comunes son el G y el H, con poca vida y capacidad ofensiva."
                    "\M, C y B son más raros, pero peligrosos. Una secuencia afortunada de sus"
                    "ataques acabará con facilidad con el jugador.",
        "combate": "Al aparecer un enemigo, el jugador puede atacar con sendas armas de las que dispone. En ambos casos"
                   ", el procedimiento es el que sigue:\n1. Se debe obtener una tirada >= al valor de impacto."
                   "\n2. Se debe superar la tirada de herida. Cuanto mayor la proporción entre la capacidad de herir "
                   "del arma y la resistencia del atacante, más fácil la tirada.\n3. Si impacta y hiere, el atacado"
                   "realiza una tirada de salvación. Debe obtener una tirada >= al valor de salvación, aplicando el "
                   "modificador de penetración. (SV de 2 con AP -3: tirada de 5+)."
                   "\n4. Si todo lo anterior triunfa, el objetivo recibe el daño indicado en D."
                   "\nLa misma secuencia se aplica cuando el enemigo ataca al jugador."
    }
    print("Bienvenido a la ayuda. Estas son las entradas disponibles.")
    print("Introduce cualquiera de ellas para ver la información asociada.")
    print("Para salir de la ayuda, introduce 'salir'")

    for entrad in wiki.keys():
        print(entrad)   # Se muestran las claves del diccionario (las entradas)
    while True:
        entrada_usuario = entrada(modo, file).lower()
        if entrada_usuario == "salir":  # Se sale de la ayuda mediante este comando
            break
        else:
            try:
                print(wiki[entrada_usuario])
            except Exception as e:
                # print(e)
                print('Entrada no reconocida. Pruebe de nuevo.')


'''
Acorde al modo elegido por el usuario,
solicita una entrada a éste (interactivo)
o toma un comando del fichero indicado.
'''
def entrada(mode, file):
    if mode == 1:
        return input()
    elif mode == 2:
        return file.readline().replace("\n", "")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    interprete()
