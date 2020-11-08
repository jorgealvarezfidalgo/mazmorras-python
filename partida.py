import dado
import enemigos


'''Representa la partida, contiene las entidades participantes y sus estados'''
class Partida:

    """Únicamenter recibe el jugador, generado por el usuario."""
    def __init__(self, jugador):
        self.enemigo = None             # Enemigo que potencialmente aparecerá
        self.peligro = False            # Situación de peligro (hay enemigo atacando)
        self.jugador = jugador
        self.turno = True               # Indica si es el turno del jugador
        self.activa = True              # Indica si el jugador está vivo
        self.desastreOcurrido = False   # Indica si ha tenido lugar un desastre

    '''Recibe un comando del intérprete y genera el código para que el jugador lo ejecute, si es su turno'''
    def accion_jugador(self, accion):
        if self.turno:
            exec('self.jugador.accion_{}(self)'.format(accion))

    '''Genera una nueva sala del laberinto.'''
    def nuevaSala(self):
        print("\nEntras a una NUEVA SALA.")
        self.jugador.reiniciar()    # El jugador recupera acciones y cura
        prob = dado.und100()
        if prob < 70:   # Lo más probable es la aparición de un enemigo
            self.desastreOcurrido = False   # El desastre ya no es el último evento
            self.crearEnemigo()
        elif 70 < prob < 80 and not self.desastreOcurrido:  # Si el último suceso no es un desastre...
            self.desastre()     # Evento aleatorio
        elif 80 < prob < 90:
            self.desastreOcurrido = False
            self.ayuda()        # Evento aleatorio
        else:
            self.desastreOcurrido = False
            print("La sala está vacía. O eso parece...")    # Sin eventos

    '''Cambia de turno. Reinicia el jugador.'''
    def nuevoTurno(self):
        self.turno = not self.turno
        self.jugador.reiniciar()

    '''Crea un enemigo en la sala.'''
    def crearEnemigo(self):
        self.peligro = True     # Hay peligro
        prob = dado.und100()
        if prob < 30:
            self.enemigo = enemigos.G()   # Lo más probable es un G
        elif 30 < prob < 60:
            self.enemigo = enemigos.H()    # O un H, los más débiles
        elif 70 < prob < 80:
            self.enemigo = enemigos.B()     # El resto son más duros, por ende, más raros
        elif 80 < prob < 95:
            self.enemigo = enemigos.C()
        else:
            self.enemigo = enemigos.M()
        print("¡De las sombras, aparece un {}!".format(type(self.enemigo).__name__))

    '''Evento aleatorio negativo para el jugador. Podría ser un listado aleatorio, por ahora, sólo uno.'''
    def desastre(self):
        print("¡Desastre! Has caído en una CENSURADO PARA DESCLASIFICACIÓN. Pierdes una herida.")
        self.jugador.reducirSalud(dado.tirada_minima)   # Se pierde salud
        print("Huyes rápidamente de la sala. No tienes tiempo de realizar otras acciones.")
        self.jugador.acciones = 0       # Se eliminan las acciones, forzando a que cambie de sala al comprobar estado
        self.desastreOcurrido = True    # Marcamos como desastre ocurrido, para que no ocurran 2+ seguidos.

    '''Evento aleatorio positivo. Recupera salud máxima'''
    def ayuda(self):
        print("CENSURADO PARA DESCLASIFICACIÓN Recobras toda tu salud por intervención sagrada.")
        self.jugador.vida = self.jugador.maxVida

    '''Se elimina al enemigo y se acaba el peligro'''
    def destruirEnemigo(self):
        self.enemigo = None
        self.peligro = False

    '''Comprueba el estado de la partida y actúa en consecuencia.'''
    def comprobarEstado(self):
        self.comprobarVida()    # Comprobamos que el jugador sigue vivo
        if not self.activa:     # Si no, se acaba la partida
            return
        if self.peligro:        # Enemigo presente
            if self.jugador.acciones == 0:  # Si no quedan acciones, turno del enemigo
                self.nuevoTurno()
            if self.enemigo.vida <= 0:  # Sin vida, el enemigo se destruye.
                print("\nEl {} ha sido justamente purgado.".format(type(self.enemigo).__name__))
                print("CENSURADO PARA DESCLASIFICACIÓN.\n")
                self.destruirEnemigo()
                self.turno = True       # Turno del jugador
            if not self.turno:          # Turno enemigo
                print("")
                print("TURNO DEL ENEMIGO")
                self.enemigo.atacar(self)
                self.enemigo.reiniciar()    # Recupera valores base
                self.nuevoTurno()
        elif self.jugador.acciones == 0:    # Sin enemigo ni acciones, le obligamos a moverse.
            print("El tiempo corre en su contra. Falto de opciones, el Aniquilador se mueve.")
            self.nuevaSala()
        self.comprobarVida()     # Comprobamos vida de nuevo (puede haber muerto durante el ataque enemigo)

    '''Comprobar vida del jugador. Si no queda, se indica y la partida acaba.'''
    def comprobarVida(self):
        if self.jugador.vida <= 0:
            print("\nEl Aniquilador {} ha sido exterminado por los alienígenas.".format(
                self.jugador.nombre
            ))
            self.activa = False


