from typing import Callable

from dado import tirada_minima, tiradas_dado

"""
Define las armas empleadas tanto por el jugador como sus enemigos.
Elemento clave a la hora de resolver el combate.
"""


class Arma:

    """Constructor. Salvo el nombre, todos los parámetros tienen un valor por defecto."""
    def __init__(self, nombre: str, imp: int = 3, her: int = 4, dmg: Callable = tirada_minima,
                 ap: int = 0, efectopas: Callable = None, efectoact: Callable = None) -> None:
        self.nombre: str = nombre
        self.impacto: int = imp         # Capacidad de impacto. Cuanto menor, mayores las posibilidades.
        self.herir: int = her           # Capacidad de herir. Cuanto mayor, mayores las posibilidades.
        self.damage: Callable = dmg     # Función que define el daño. Puede ser un valor fijo o aleatorio.
        self.ap: int = ap               # Penetración de armadura. Modificador sobre la salvación del objetivo.
        self.efectopas: Callable = efectopas    # Efecto pasivo. Actúa al equiparse, sobre el jugador
        self.efectoact: Callable = efectoact    # Efecto activo. Actúa al golpear, sobre el enemigo

    '''
    Redefinimos el string para que al imprimir el listado de armas se muestren las estadísticas
    con un formato adecuado.
    '''
    def __repr__(self) -> str:
        ntabs: int = int((len(self.nombre) - 4) / 4)
        nesp: int = (len(self.nombre) - 4) % 4
        tabs: str = ""
        for i in range(ntabs):
            tabs += "\t"
        for i in range(nesp):
            tabs += " "
        dam_name: str = self.damage.__name__
        header: str = "Arma{}\tI\tH\tD\tAP\n".format(tabs)
        return "{}{}\t{}\t{}\t{}\t{}".format(header, self.nombre, self.impacto, self.herir,
                                             tiradas_dado[dam_name], self.ap)

    '''
    Ejecuta el efecto pasivo del arma, si existe.
    '''
    def efecto_pasivo(self) -> None:
        cond: bool = self.efectopas is not None
        if cond:
            self.efectopas()
