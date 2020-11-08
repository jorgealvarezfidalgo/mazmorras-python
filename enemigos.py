import dado
import combate
from arma import Arma

'''Clase base de las entidades enemigas. 
Similar a la entidad jugador, con capacidad de realizar varios ataques.
'''


class T:
    """El constructor recibe mayor nº de parámetros para crear el arma estándar a cada subclase."""

    def __init__(self, vida, imp, her, resistencia, dmg, ap, sv, ataques, ea=None):
        self.vida = vida
        self.impactoBase = imp  # Se guardan los valores originales de campos modificables por el jugador
        self.resistencia = resistencia
        self.apbase = ap  # Se guardan los valores originales de campos modificables por el jugador
        self.save = sv
        self.ataques = ataques  # Ataques que realizará en cada turno
        self.arma = Arma('Garras', imp, her, dmg, ap, efectoact=ea)  # Arma genérica de cuerpo a cuerpo.

    '''Se reduce la salud del tiránido en lo que determine la función pasada por parámetro'''
    def reducirSalud(self, damage):  # damage es Función de primer orden
        heridas = damage()
        self.vida -= heridas
        return heridas

    '''
    Realiza tantos ataques al jugador como determine el valor. 
    El ataque se resuelve del mismo modo que los ataques del jugador.
    '''
    def atacar(self, part):
        for i in range(self.ataques):
            print("Ataque {}".format(i + 1))
            combate.resolver_ataque(self.arma, part.jugador)

    '''
    Reinicia los atributos modificables a sus valores originales.
    Permite recuperar a final de turno los valores modificados por las habilidades del jugador.
    '''
    def reiniciar(self):
        self.arma.impacto = self.impactoBase
        self.arma.ap = self.apbase


'''
A continuación se crean diversas subclases del enemigo base, que serán las que aparezcan en la partida.
En esta versión solo varían en las estadísticas, pero la idea reside en permitir expandir 
futuras habilidades y acciones únicas para cada clase; que por restricciones temporales, 
no es posible para esta entrega.
'''


class G(T):

    def __init__(self):
        super().__init__(1, 3, 4, 4, dado.tirada_minima, -1, 4, 4)


class H(T):

    def __init__(self):
        super().__init__(1, 4, 3, 3, dado.und2, 0, 6, 3)


class M(T):

    def __init__(self):
        super().__init__(12, 4, 7, 7, dado.und6, -3, 3, 2)


class C(T):

    def __init__(self):
        super().__init__(8, 4, 6, 7, dado.d3, -3, 3, 3)


class B(T):

    def __init__(self):
        super().__init__(6, 2, 5, 5, dado.und3, -3, 4, 3)
