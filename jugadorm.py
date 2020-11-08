import copy

from arma import Arma
from functools import partial
import dado
import combate


'''Clase base del jugador.'''
class Aniquilador:

    """Recibe como parámetros los datos personales. El resto de atr. se inicializan por defecto y no son modificables
    durante la configuración; sí como consecuencia de los hechos de la partida. """
    def __init__(self, nombre, capitulo):
        self.nombre = nombre
        self.capitulo = capitulo
        self.vida = 5
        self.maxVida = 5            # Guardamos la vida base para conocer su límite en las curaciones.
        self.save = 3
        self.resistencia = 4
        self.arma_cc = None         # Arma cuerpo a cuerpo seleccionada del listado.
        self.armas_cc = []          # Listado de armas cuerpo a cuerpo (cada subclase tiene distinto)
        self.arma_dis = None        # Arma a distancia seleccionada del listado.
        self.armas_dis = []         # Listado de armas a distancia (cada subclase tiene distinto)
        self.acciones = 4
        self.accionesBase = 4       # Guardamos las acciones base para recobrarlas en cada turno
        self.cura_usada = False     # Permite impedir que se abuse de las curaciones (p.e. en sala vacía).

    '''Realiza un ataque al enemigo mediante el arma cuerpo a cuerpo.'''
    def accion_golpear(self, part):     # name_mangling
        self.acciones -= 1  # Consume una acción
        print("Atacando cuerpo a cuerpo con {}.".format(self.arma_cc.nombre))
        combate.resolver_ataque(self.arma_cc, part.enemigo)

    '''Realiza un ataque al enemigo mediante el arma a distancia.'''
    def accion_disparar(self, part):    # name_mangling
        self.acciones -= 1  # Consume una acción
        print("Atacando a distancia con {}.".format(self.arma_dis.nombre))
        combate.resolver_ataque(self.arma_dis, part.enemigo)

    '''Si no hay enemigo presente, mueve al jugador a una nueva sala.'''
    def accion_mover(self, part):       # name_mangling
        if not part.peligro:
            part.nuevaSala()    # No consume acción (para que no se quede atascado si las agota sin peligro)
        else:
            print("No puedes cambiar de sala mientras estás combatiendo.")

    '''Cura una herida al jugador. Un único uso por turno.'''
    def accion_curar(self, part=None):  # name_mangling
        if self.cura_usada:
            print("No se pueden realizar más curaciones en este turno.")
        elif self.vida < self.maxVida:  # No se puede curar más de la vida base.
            self.acciones -= 1          # Consume una acción
            print("Tu servoarmadura realiza reparaciones a nivel microcelular. Recuperas una herida.")
            self.vida += 1
            self.cura_usada = True      # Se marca como usada.
        else:
            print("Ya posees la máxima salud.")

    '''Reduce la salud del jugador en lo indicado por la función damage'''
    def reducirSalud(self, damage):  # Función de primer orden
        heridas = damage()
        self.vida -= heridas
        return heridas

    '''Se reinician las estadísticas para un nuevo turno: se recuperan acciones y cura.'''
    def reiniciar(self):
        self.acciones = self.accionesBase
        self.cura_usada = False

    '''Duplica las acciones disponibles durante el resto de la partida.'''
    def duplicarAcciones(self):
        print("Característica especial desbloqueada: tus ataques se duplican.")
        self.acciones *= 2
        self.accionesBase *= 2

    '''Muestra por pantalla la actual via y acciones.'''
    def estado_actual(self):
        print("Vida restante: {}.".format(self.vida))
        print("Acciones restantes: {}.\n".format(self.acciones))

    '''Dado un índice, si existe tal en el listado de armas cuerpo a cuerpo, la selecciona como arma cc a usar.'''
    def elegir_arma_cc(self, index):
        if 0 <= index < len(self.armas_cc):
            self.arma_cc = copy.deepcopy(self.armas_cc[index])
            # Copia profunda para que las modificaciones que afecten al arma no modifiquen la original del listado
            # puesto que la necesitaremos como referencia para recuperar los valores originales

    '''Dado un índice, si existe tal en el listado de armas a distancia, la selecciona como arma a dis. a usar.'''
    def elegir_arma_dis(self, index):
        if 0 <= index < len(self.armas_dis):
            self.arma_dis = copy.copy(self.armas_dis[index])

    '''Devuelve el nombre de la clase, ortográficamente correcto para mostrar en la selección de clase.'''
    @staticmethod
    def getNombreClase():
        return "Aniquilador"


class Capellan(Aniquilador):

    """El Capellán posee sendos tipos de arma, pero de estadísticas poco notables. No obstante, es
    capaz de realizar litanías de batalla que otorgan efectos especiales."""
    def __init__(self, nombre, capitulo):
        super().__init__(nombre, capitulo)
        self.armas_cc = [Arma('CA', imp=2, her=5, dmg=dado.d2, ap=-1)]
        self.armas_dis = [Arma('BA')]

    '''Acción única del capellán. Si es exitosa, ejecuta efectos especiales sobre sí o el enemigo.'''
    def accion_litania(self, part):  # name_mangling
        if not part.peligro:        # Necesita de un enemigo presente.
            print("El capellán reza al CENSURADO PARA DESCLASIFICACIÓN en silencio. Sin enemigos presentes, no hay bonificaciones.")
        else:
            self.acciones -= 1      # Consume una acción
            print("El capellán realiza plegarias al CENSURADO PARA DESCLASIFICACIÓN solicitando su divina ayuda.")
            if combate.x_o_mas(3):  # Tirada de 3+
                exec("self._realizar_litania{}()".format(str(dado.und3()))) # Se escoge aleatoriamente la litanía
            else:
                print("La litanía ha fracasado.")

    '''Esta litanía provee de dos acciones extra este turno al capellán.'''
    def _realizar_litania1(self):
        print("¡La divina inspiración te posee! Tus movimientos se vuelven raudos y certeros.")
        print("Recibes dos acciones extra.")
        self.acciones += 2

    '''Esta litanía provee de +3 herir y daño D3 al arma cuerpo a cuerpo este turno.'''
    def _realizar_litania2(self):
        print("El CENSURADO PARA DESCLASIFICACIÓN bendice tu CA. Mayor fuerza y daño en este turno.")
        self.arma_cc.herir = 8
        self.arma_cc.damage = dado.d3

    '''Esta litanía limita el impacto y AP del arma enemiga.'''
    def _realizar_litania3(self):
        print("El CENSURADO PARA DESCLASIFICACIÓN bendice tu CA. Su brillo arcano confunde al enemigo.")
        print("Con el próximo golpe, el enemigo pierde estadísticas de ataque.")
        self.arma_cc.efectoact = partial(combate.aplicar_efecto, mod=lambda x: x + 2,
                                         ats=["arma.impacto", "arma.ap"])

    '''
    Además de reiniciar los atributos establecidos en el padre, toma de nuevo el arma original para
    deshacer los efectos de la litanía. De ahí la importancia del deepcopy() previo.
    '''
    def reiniciar(self):
        super(Capellan, self).reiniciar()
        self.elegir_arma_cc(0)

    @staticmethod
    def getNombreClase():
        return "Capellán"


class Tactico(Aniquilador):

    """El Táctico posee la mayor variedad de armas a distancia y las más efectivas."""
    def __init__(self, nombre, capitulo):
        super().__init__(nombre, capitulo)
        self.armas_cc = [Arma('PC', her=8, dmg=dado.und3)]
        self.armas_dis = [Arma('BT'),
                          Arma('CñA', her=6, dmg=dado.und6),
                          Arma('L', imp=0, her=5, dmg=dado.und3, ap=-1)]

    @staticmethod
    def getNombreClase():
        return "Táctico"


class Asalto(Aniquilador):

    """Asalto posee mayor fuerza vital y se especializa en el cuerpo a cuerpo, pero carece de armamento a distancia."""
    def __init__(self, nombre, capitulo):
        super().__init__(nombre, capitulo)
        self.armas_cc = [Arma('CR', dmg=dado.und2, ap=-2, efectopas=self.duplicarAcciones),
                         Arma('MT', imp=4, her=8, dmg=dado.d3, ap=-3)]
        self.armas_dis = []
        self.vida = 7
        self.maxVida = 7
        self.save = 2

    '''Sobreescribimos la acción de disparo, puesto que no es posible con esta clase.'''
    def accion_disparar(self, part):
        print("La clase Asalto carece de armas de disparo")

    @staticmethod
    def getNombreClase():
        return "Asalto"
