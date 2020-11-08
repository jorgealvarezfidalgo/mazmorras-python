import unittest
from functools import partial
import io
import sys

import jugadorm
from partida import Partida
import dado
import enemigos
from arma import Arma
import combate


class Test(unittest.TestCase):

    def setUp(self):
        self.testAsalto = jugadorm.Asalto("S", "PI")
        self.testCapellan = jugadorm.Capellan("G", "TN")
        self.testTactico = jugadorm.Tactico("T", "CS")

        self.testPartidaAs = Partida(self.testAsalto)
        self.testPartidaCa = Partida(self.testCapellan)
        self.testPartidaTa = Partida(self.testTactico)

    def tearDown(self):
        pass

    def capturePrint(self):
        # Capturar el print
        capturedOutput = io.StringIO()  # Crear objeto StringIO
        sys.stdout = capturedOutput  # Redirigir stdout.
        return capturedOutput

    def test_dado(self):
        # Funcionamiento esperado de todas las tiradas
        self.assertEqual(dado.d3(), 3)
        self.assertTrue(1 <= dado.und3() <= 3)
        self.assertEqual(dado.d2(), 2)
        self.assertTrue(1 <= dado.und3() <= 3)
        self.assertTrue(1 <= dado.und2() <= 2)
        self.assertTrue(1 <= dado.und100() <= 100)
        self.assertEqual(dado.tirada_minima(), 1)
        pass

    def test_arma(self):
        self.arma1 = Arma('CA', imp=2, her=5, dmg=dado.d2, ap=-1)

        # El único parámetro obligatorio es el nombre
        self.arma2 = Arma('BA')
        jugador = jugadorm.Asalto("A", "CS")

        # Arma con efecto pasivo; se ejecuta al equipar
        self.arma3 = Arma('CR', dmg=dado.und2, ap=-2,
                          efectopas=jugador.duplicarAcciones)

        # Arma con efecto activo; se ejecuta al golpear
        # Reduce el atributo herir del enemigo en 1
        self.arma4 = Arma('L', imp=0, her=5, dmg=dado.und3, ap=-1,
                          efectoact=partial(combate.aplicar_efecto, mod=lambda x: x - 1,
                                            ats=["resistencia"])
                          )

        # Comprobamos que el string, daño y efecto son los esperados
        self.assertEqual(str(self.arma1), "Arma  \tI\tH\tD\tAP\nCA\t2\t5\t2\t-1")
        self.assertEqual(self.arma1.damage(), 2)
        self.assertEqual(self.arma1.efecto_pasivo(), None)

        self.assertEqual(str(self.arma2), "Arma  \tI\tH\tD\tAP\nBA\t3\t4\t1\t0")
        self.assertEqual(self.arma2.damage(), 1)
        self.assertEqual(self.arma2.efecto_pasivo(), None)

        self.assertEqual(str(self.arma3), "Arma  \tI\tH\tD\tAP\nCR\t3\t4\tD2\t-2")
        self.assertTrue(1 <= self.arma3.damage() <= 2)
        # Comprobamos el correcto funcionamiento del efecto pasivo
        self.arma3.efecto_pasivo()
        self.assertEqual(jugador.acciones, 8)

        self.assertEqual(str(self.arma4), "Arma \tI\tH\tD\tAP\nL\t0\t5\tD3\t-1")
        self.assertTrue(1 <= self.arma4.damage() <= 3)
        self.assertEqual(self.arma4.efecto_pasivo(), None)

        # Comprobamos el efecto activo. Necesita atacar a un enemigo.
        enemigo = enemigos.H()
        self.assertEqual(enemigo.resistencia, 3)
        self.testTactico.arma_dis = self.arma4
        combate.resolver_ataque(self.testTactico.arma_dis, enemigo)
        self.assertEqual(enemigo.resistencia, 2)    # Reduce el valor en 1

    def test_combate(self):
        # Un 1+ triunfa siempre, un 7+ fracasa siempre
        self.assertTrue(combate.x_o_mas(1))
        self.assertFalse(combate.x_o_mas(7))

        # Una salvación de 1+ sería siempre favorable
        self.assertTrue(combate.salva(1, 0))
        # Las siguientes combinaciones de SV y AP fallarán siempre
        self.assertFalse(combate.salva(6, -1))
        self.assertFalse(combate.salva(5, -2))
        self.assertFalse(combate.salva(4, -3))
        self.assertFalse(combate.salva(3, -4))
        # El resto dependen de la tirada

        # hiere() nunca devuelve un resultado fijo.
        # No obstante, podemos comprobar la tirada que realiza según los valores recibidos
        self.assertEqual(combate.calcular_prop(4, 4), 4)
        self.assertEqual(combate.calcular_prop(5, 4), 3)
        self.assertEqual(combate.calcular_prop(4, 5), 5)
        self.assertEqual(combate.calcular_prop(8, 4), 2)
        self.assertEqual(combate.calcular_prop(4, 8), 6)

        enemigo = enemigos.G()
        jugador = self.testAsalto
        self.testAsalto.elegir_arma_cc(1)

        co = self.capturePrint()
        combate.resolver_ataque(jugador.arma_cc, None)
        self.assertEqual(co.getvalue(),
                         "En un arrebato de furia, atacas el mobiliario de la sala. "
                         "Un acto que no provee de mayor gloria al CENSURADO PARA DESCLASIFICACIÓN.\n"
                         )

        # Hagamos que fracase el impacto
        co = self.capturePrint()
        self.testAsalto.arma_cc.impacto = 7
        combate.resolver_ataque(jugador.arma_cc, enemigo)
        self.assertEqual(co.getvalue(),
                         "No se ha conseguido impactar al G.\n"
                         )
        self.testAsalto.arma_cc.impacto = 1

        # El herir. Siempre tiene una posibilidad de herir, así que realizamos un bucle.
        co = self.capturePrint()
        enemigo.resistencia = 8
        loop = 0
        while co.getvalue() != "No se ha conseguido herir al G.\n":
            co = self.capturePrint()
            combate.resolver_ataque(jugador.arma_cc, enemigo)
            loop += 1
            self.assertTrue(loop < 1000, "Se han realizado demasiados intentos exitosos de herir."
                                         "Debería tener una probabilidad de fallo de 5/6")
        self.assertEqual(co.getvalue(), "No se ha conseguido herir al G.\n")

        co = self.capturePrint()
        enemigo.resistencia = 1
        enemigo.save = -10
        loop = 0
        while co.getvalue() != "Se ha impactado y herido al G.\n" \
                               "El G regenera sus tejidos celulares y salva sus heridas.\n":
            co = self.capturePrint()
            combate.resolver_ataque(jugador.arma_cc, enemigo)
            loop += 1
            self.assertTrue(loop < 1000, "Se han realizado demasiados intentos fallidos de herir."
                                         "Debería tener una probabilidad de éxito de 5/6")
        self.assertEqual(co.getvalue(), "Se ha impactado y herido al G.\n"
                                        "El G regenera sus tejidos celulares y salva sus heridas.\n")

        # Impacta, hiere y no salva
        enemigo.save = 7
        loop = 0
        while co.getvalue() != "Se ha impactado y herido al G.\n" \
                               "El G recibe 3 heridas.\n":
            co = self.capturePrint()
            combate.resolver_ataque(jugador.arma_cc, enemigo)
            loop += 1
            self.assertTrue(loop < 1000, "Se han realizado demasiados intentos fallidos de herir."
                                         "Debería tener una probabilidad de éxito de 5/6")
        self.assertEqual(co.getvalue(), "Se ha impactado y herido al G.\n"
                                        "El G recibe 3 heridas.\n")

    def test_enemigos(self):
        G = enemigos.G()
        H = enemigos.H()
        M = enemigos.M()
        C = enemigos.C()
        B = enemigos.B()

        # Los datos varían, pero las comprobaciones para todos ellos siguen la misma estructura

        # Comprobar que pierde vida
        self.assertEqual(G.vida, 1)
        G.reducirSalud(dado.tirada_minima)
        self.assertEqual(G.vida, 0)

        # El daño es el esperado
        self.assertEqual(G.arma.damage(), 1)

        # Nº de ataques esperado
        co = self.capturePrint()
        G.atacar(self.testPartidaAs)
        self.assertTrue("Ataque 1\n" in co.getvalue())
        self.assertTrue("Ataque 2\n" in co.getvalue())
        self.assertTrue("Ataque 3\n" in co.getvalue())
        self.assertTrue("Ataque 4\n" in co.getvalue())
        self.testPartidaAs.jugador.vida = self.testPartidaAs.jugador.maxVida

        # Cambiar valores de ats. susceptibles y comprobar que son reiniciados a la base
        G.arma.impacto = 5
        G.arma.ap = 0
        G.reiniciar()
        self.assertEqual(G.arma.impacto, 3)
        self.assertEqual(G.arma.ap, -1)

        # Repetir para los demás

        self.assertEqual(H.vida, 1)
        H.reducirSalud(dado.tirada_minima)
        self.assertEqual(H.vida, 0)

        self.assertTrue(1 <= H.arma.damage() <= 2)

        co = self.capturePrint()
        H.atacar(self.testPartidaAs)
        self.assertTrue("Ataque 1\n" in co.getvalue())
        self.assertTrue("Ataque 2\n" in co.getvalue())
        self.assertTrue("Ataque 3\n" in co.getvalue())
        self.testPartidaAs.jugador.vida = self.testPartidaAs.jugador.maxVida

        H.arma.impacto = 5
        H.arma.ap = -1
        H.reiniciar()
        self.assertEqual(H.arma.impacto, 4)
        self.assertEqual(H.arma.ap, 0)

        self.assertEqual(M.vida, 12)
        M.reducirSalud(lambda: 5)
        self.assertEqual(M.vida, 7)

        self.assertTrue(1 <= M.arma.damage() <= 6)

        co = self.capturePrint()
        M.atacar(self.testPartidaAs)
        self.assertTrue("Ataque 1\n" in co.getvalue())
        self.assertTrue("Ataque 2\n" in co.getvalue())
        self.testPartidaAs.jugador.vida = self.testPartidaAs.jugador.maxVida

        M.arma.impacto = 5
        M.arma.ap = 0
        M.reiniciar()
        self.assertEqual(M.arma.impacto, 4)
        self.assertEqual(M.arma.ap, -3)

        self.assertEqual(C.vida, 8)
        C.reducirSalud(lambda: 8)
        self.assertEqual(C.vida, 0)

        self.assertEqual(C.arma.damage(), 3)

        co = self.capturePrint()
        C.atacar(self.testPartidaAs)
        self.assertTrue("Ataque 1\n" in co.getvalue())
        self.assertTrue("Ataque 2\n" in co.getvalue())
        self.assertTrue("Ataque 3\n" in co.getvalue())
        self.testPartidaAs.jugador.vida = self.testPartidaAs.jugador.maxVida

        C.arma.impacto = 5
        C.arma.ap = -2
        C.reiniciar()
        self.assertEqual(C.arma.impacto, 4)
        self.assertEqual(C.arma.ap, -3)

        self.assertEqual(B.vida, 6)
        B.reducirSalud(lambda: 7)
        self.assertEqual(B.vida, -1)
        B.reiniciar()

        self.assertTrue(1 <= B.arma.damage() <= 3)

        co = self.capturePrint()
        B.atacar(self.testPartidaAs)
        self.assertTrue("Ataque 1\n" in co.getvalue())
        self.assertTrue("Ataque 2\n" in co.getvalue())
        self.assertTrue("Ataque 3\n" in co.getvalue())
        self.testPartidaAs.jugador.vida = self.testPartidaAs.jugador.maxVida

        B.arma.impacto = 1
        B.arma.ap = -4
        B.reiniciar()
        self.assertEqual(B.arma.impacto, 2)
        self.assertEqual(B.arma.ap, -3)

    def test_jugador(self):

        # Estado inicial
        for jugador in [self.testCapellan, self.testTactico]:
            self.assertEqual(jugador.vida, 5)
            self.assertEqual(jugador.maxVida, 5)
            self.assertEqual(jugador.save, 3)
            self.assertEqual(jugador.resistencia, 4)
            self.assertEqual(jugador.acciones, 4)
            self.assertEqual(jugador.accionesBase, 4)
            self.assertEqual(jugador.cura_usada, False)

        self.assertEqual(self.testAsalto.vida, 7)
        self.assertEqual(self.testAsalto.maxVida, 7)
        self.assertEqual(self.testAsalto.save, 2)
        self.assertEqual(self.testAsalto.resistencia, 4)
        self.assertEqual(self.testAsalto.acciones, 4)
        self.assertEqual(self.testAsalto.accionesBase, 4)
        self.assertEqual(self.testAsalto.cura_usada, False)

        # Curar
        for jugador in [self.testAsalto, self.testCapellan, self.testTactico]:
            jugador.reducirSalud(dado.tirada_minima)
            self.assertEqual(jugador.vida, jugador.maxVida - 1)
            co = self.capturePrint()
            jugador.accion_curar()
            self.assertEqual(jugador.vida, jugador.maxVida)
            self.assertEqual(co.getvalue(), "Tu servoarmadura realiza reparaciones a nivel microcelular. "
                                            "Recuperas una herida.\n")
            co = self.capturePrint()
            jugador.accion_curar()
            self.assertEqual(jugador.vida, jugador.maxVida)
            self.assertEqual(co.getvalue(), "No se pueden realizar más curaciones en este turno.\n")

            jugador.reiniciar()
            co = self.capturePrint()
            jugador.accion_curar()
            self.assertEqual(jugador.vida, jugador.maxVida)
            self.assertEqual(co.getvalue(), "Ya posees la máxima salud.\n")

        # Duplicar acciones
        for jugador in [self.testAsalto, self.testCapellan, self.testTactico]:
            jugador.duplicarAcciones()
            self.assertEqual(jugador.acciones, 8)
            self.assertEqual(jugador.accionesBase, 8)
            jugador.accionesBase = 4
            jugador.reiniciar()
            self.assertEqual(jugador.acciones, 4)
            self.assertEqual(jugador.accionesBase, 4)

        # Estado actual
        for jugador in [self.testCapellan, self.testTactico]:
            co = self.capturePrint()
            jugador.estado_actual()
            self.assertEqual(co.getvalue(), "Vida restante: 5.\nAcciones restantes: 4.\n\n")

        co = self.capturePrint()
        self.testAsalto.estado_actual()
        self.assertEqual(co.getvalue(), "Vida restante: 7.\nAcciones restantes: 4.\n\n")

    def test_disparar(self):
        # Comprobar ataque a distancia del Capellán
        self.testPartidaCa.enemigo = enemigos.G()
        self.testCapellan.elegir_arma_dis(0)
        co = self.capturePrint()
        self.testCapellan.accion_disparar(self.testPartidaCa)

        self.assertEqual(self.testCapellan.acciones, self.testCapellan.accionesBase - 1)
        wo = co.getvalue()
        self.assertTrue("Atacando a distancia con BA.\n" in co.getvalue())

        # Comprobar ataque a distancia con todas las armas del Táctico
        acciones = self.testTactico.accionesBase
        for arma in self.testTactico.armas_dis:
            self.testPartidaTa.enemigo = enemigos.G()
            self.testTactico.arma_dis = arma
            co = self.capturePrint()
            self.testTactico.accion_disparar(self.testPartidaTa)
            acciones -= 1
            self.assertEqual(self.testTactico.acciones, acciones)
            self.assertTrue("Atacando a distancia con {}.\n".format(arma.nombre) in co.getvalue())

        # Comprobar que Asalto no dispara
        co = self.capturePrint()
        self.testAsalto.accion_disparar(self.testPartidaAs)
        self.assertEqual(co.getvalue(), "La clase Asalto carece de armas de disparo\n")

    def test_golpear(self):
        # Comprobar ataque cuerpo a cuerpo del Capellán
        self.testPartidaCa.enemigo = enemigos.H()
        self.testCapellan.elegir_arma_cc(0)
        co = self.capturePrint()
        self.testCapellan.accion_golpear(self.testPartidaCa)

        self.assertEqual(self.testCapellan.acciones, self.testCapellan.accionesBase - 1)
        self.assertTrue("Atacando cuerpo a cuerpo con CA.\n" in co.getvalue())

        # Comprobar ataque c-c con todas las armas del Táctico
        acciones = self.testTactico.accionesBase
        for arma in self.testTactico.armas_cc:
            self.testPartidaTa.enemigo = enemigos.H()
            self.testTactico.arma_cc = arma
            co = self.capturePrint()
            self.testTactico.accion_golpear(self.testPartidaTa)
            acciones -= 1
            self.assertEqual(self.testTactico.acciones, acciones)
            self.assertTrue("Atacando cuerpo a cuerpo con {}.\n".format(arma.nombre) in co.getvalue())

        # Comprobar ataque c-c con todas las armas del Asalto
        acciones = self.testAsalto.accionesBase
        for arma in self.testAsalto.armas_cc:
            self.testPartidaAs.enemigo = enemigos.H()
            self.testAsalto.arma_cc = arma
            co = self.capturePrint()
            self.testAsalto.accion_golpear(self.testPartidaAs)
            acciones -= 1
            self.assertEqual(self.testAsalto.acciones, acciones)
            self.assertTrue("Atacando cuerpo a cuerpo con {}.\n".format(arma.nombre) in co.getvalue())

    def test_mover(self):
        # Para todas las clases
        jugadores = [self.testAsalto, self.testCapellan, self.testTactico]
        partidas = [self.testPartidaAs, self.testPartidaCa, self.testPartidaTa]
        for i in range(len(jugadores)):
            jugador = jugadores[i]
            partida = partidas[i]
            # No se puede mover si hay enemigo
            partida.crearEnemigo()
            co = self.capturePrint()
            jugador.accion_mover(partida)
            self.assertEqual(co.getvalue(), "No puedes cambiar de sala mientras estás combatiendo.\n")

            # Sin enemigo, se mueve
            partida.destruirEnemigo()
            jugador.accion_mover(partida)
            self.assertTrue("\nEntras a una NUEVA SALA.\n" in co.getvalue())

    def test_litania(self):
        self.testCapellan.elegir_arma_cc(0)
        # Sin enemigos, no realiza efecto
        co = self.capturePrint()
        self.testCapellan.accion_litania(self.testPartidaCa)
        self.assertEqual(co.getvalue(), "El capellán reza al CENSURADO PARA DESCLASIFICACIÓN en silencio. Sin enemigos presentes, "
                                        "no hay bonificaciones.\n")

        # Puesto que las litanías (o su fracaso) se realiza aleatoriamente, las hacemos varias veces
        for i in range(15):
            self.testPartidaCa.crearEnemigo()
            self.testCapellan.accion_litania(self.testPartidaCa)
            self.testCapellan.acciones = self.testCapellan.accionesBase - 1
            self.assertTrue(
                "El capellán realiza plegarias al CENSURADO PARA DESCLASIFICACIÓN solicitando su divina ayuda.\n" in co.getvalue())
            # Realizará una de las tres litanías o fracasará
            condicion = "La litanía ha fracasado.\n" in co.getvalue() \
                        or "¡La divina inspiración te posee! Tus movimientos se vuelven raudos y certeros.\n" \
                        in co.getvalue() or "El CENSURADO PARA DESCLASIFICACIÓN bendice tu CA. " \
                                            "Mayor fuerza y daño en este turno.\n" in co.getvalue() \
                        or "El CENSURADO PARA DESCLASIFICACIÓN bendice tu CA. Su brillo " \
                           "arcano confunde al enemigo.\n" in co.getvalue()
            self.assertTrue(condicion)
            self.testCapellan.reiniciar()

        # Comprobar funcionamiento de la litania 1 (afecta al Capellán)
        self.testCapellan._realizar_litania1()
        self.assertEqual(self.testCapellan.acciones, self.testCapellan.accionesBase + 2)

        # Comprobar funcionamiento de la litania 2 (afecta el arma del Capellán)
        self.assertEqual(self.testCapellan.arma_cc.herir, 5)
        self.assertEqual(self.testCapellan.arma_cc.damage, dado.d2)
        self.testCapellan._realizar_litania2()
        self.assertEqual(self.testCapellan.arma_cc.herir, 8)
        self.assertEqual(self.testCapellan.arma_cc.damage, dado.d3)

        self.testCapellan.reiniciar()
        self.assertEqual(self.testCapellan.arma_cc.herir, 5)
        self.assertEqual(self.testCapellan.arma_cc.damage, dado.d2)

        # Comprobar funcionamiento de la litania 3 (afecta al enemigo)
        self.testCapellan._realizar_litania3()
        self.testPartidaCa.enemigo = enemigos.M()
        self.assertEqual(self.testPartidaCa.enemigo.arma.impacto, 4)
        self.assertEqual(self.testPartidaCa.enemigo.arma.ap, -3)
        self.testCapellan.accion_golpear(self.testPartidaCa)
        self.assertEqual(self.testPartidaCa.enemigo.arma.impacto, 6)
        self.assertEqual(self.testPartidaCa.enemigo.arma.ap, -1)

        # Tras reiniciar (cambiar de turno), los efectos se disipan
        self.testPartidaCa.enemigo.reiniciar()
        self.assertEqual(self.testPartidaCa.enemigo.arma.impacto, 4)
        self.assertEqual(self.testPartidaCa.enemigo.arma.ap, -3)

    def test_partida(self):
        jugadores = [self.testAsalto, self.testCapellan, self.testTactico]
        partidas = [self.testPartidaAs, self.testPartidaCa, self.testPartidaTa]
        # Probar accion_jugador
        # Probar accion_jugador
        for i in range(len(jugadores)):
            partida = partidas[i]
            jugador = jugadores[i]
            jugador.elegir_arma_dis(0)
            jugador.elegir_arma_cc(0)
            for accion in ["mover", "disparar", "golpear", "curar"]:
                partida.accion_jugador(accion)

        self.testPartidaCa.accion_jugador("litania")

        for i in range(len(jugadores)):
            partida = partidas[i]
            jugador = jugadores[i]

            # Probar nuevaSala
            self.assertTrue(jugador.acciones < jugador.accionesBase)
            co = self.capturePrint()
            partida.nuevaSala()
            self.assertTrue("\nEntras a una NUEVA SALA.\n" in co.getvalue())
            if "¡Desastre!" in co.getvalue():
                self.assertEqual(jugador.acciones, 0)
            else:
                self.assertEqual(jugador.acciones, jugador.accionesBase)
            # Se producirá una de las siguientes:
            condicion = "La sala está vacía. O eso parece...\n" in co.getvalue() or \
                        "¡De las sombras, aparece un" in co.getvalue() or \
                        "¡Desastre! Has caído en una CENSURADO PARA DESCLASIFICACIÓN. Pierdes una herida.\n" \
                        in co.getvalue() \
                        or "CENSURADO PARA DESCLASIFICACIÓN Recobras toda tu salud por intervención sagrada." in co.getvalue()
            self.assertTrue(condicion)

            # Probar nuevoTurno
            jugador.acciones = jugador.accionesBase
            jugador.reducirSalud(dado.tirada_minima)
            jugador.accion_curar(partida)
            self.assertTrue(jugador.cura_usada)
            self.assertTrue(partida.turno)
            self.assertEqual(jugador.acciones, jugador.accionesBase - 1)
            partida.nuevoTurno()
            # Ya no es el turno del jugador. Este recupera la cura y las acciones.
            self.assertFalse(jugador.cura_usada)
            self.assertFalse(partida.turno)
            self.assertEqual(jugador.acciones, jugador.accionesBase)
            partida.nuevoTurno()
            self.assertTrue(partida.turno)

            # Probar crearEnemigo
            co = self.capturePrint()
            partida.crearEnemigo()
            self.assertTrue(partida.peligro)
            self.assertTrue("¡De las sombras, aparece un " in co.getvalue())
            # Uno de los siguientes enemigos:
            condicion = "G" in co.getvalue() or \
                        "H" in co.getvalue() or \
                        "B" in co.getvalue() or \
                        "C" in co.getvalue() or \
                        "M" in co.getvalue()
            self.assertTrue(condicion)
            self.assertTrue(isinstance(partida.enemigo, enemigos.T))

            # Probar destruirEnemigo
            partida.destruirEnemigo()
            self.assertFalse(partida.peligro)
            self.assertTrue(partida.enemigo is None)

            # Probar desastre
            jugador.vida = jugador.maxVida
            co = self.capturePrint()
            partida.desastre()
            self.assertTrue("¡Desastre! Has caído en una CENSURADO PARA DESCLASIFICACIÓN. Pierdes una herida.\n"
                            "Huyes rápidamente de la sala. No tienes tiempo de realizar otras "
                            "acciones.\n" in co.getvalue())
            # Perderá una herida, pero se puede curar al entrar a una nueva sala (ayuda)
            # O perderá más si suma varios desastres seguidos (poco plausible, pero posible)
            # Por tanto, no podemos determinar las heridas que tendrá

            # Probar ayuda
            jugador.vida = jugador.maxVida - 1
            co = self.capturePrint()
            partida.ayuda()
            self.assertEqual(co.getvalue(),
                             "CENSURADO PARA DESCLASIFICACIÓN Recobras toda tu salud por intervención sagrada.\n")
            self.assertEqual(jugador.vida, jugador.maxVida)

    def test_partida_estados(self):
        jugadores = [self.testAsalto, self.testCapellan, self.testTactico]
        partidas = [self.testPartidaAs, self.testPartidaCa, self.testPartidaTa]
        for i in range(len(jugadores)):
            partida = partidas[i]
            jugador = jugadores[i]

            # Aparece enemigo. El jugador está en peligro
            partida.crearEnemigo()

            # Si el jugador gasta todas las acciones, se cambia de turno
            self.assertTrue(partida.turno)
            jugador.acciones = 0
            co = self.capturePrint()
            # Si el enemigo sigue presente y es el turno contrario, éste ataca
            partida.comprobarEstado()
            self.assertTrue("\nTURNO DEL ENEMIGO\n" in co.getvalue())
            self.assertTrue("Ataque 1\n" in co.getvalue())
            # Tras finalizar el turno enemigo, vuelve a ser del jugador
            self.assertTrue(partida.turno)
            # Y recupera las acciones
            self.assertEqual(jugador.acciones, jugador.accionesBase)

            # Si el enemigo pierde la vida, desaparece
            jugador.vida = jugador.maxVida
            partida.enemigo.vida = 0
            partida.activa = True
            co = self.capturePrint()
            partida.comprobarEstado()
            self.assertTrue("ha sido justamente purgado." in co.getvalue())
            self.assertTrue("CENSURADO PARA DESCLASIFICACIÓN" in co.getvalue())
            self.assertEqual(partida.enemigo, None)
            self.assertFalse(partida.peligro)

            # Jugador sin acciones restantes y enemigo sin vida
            partida.crearEnemigo()
            jugador.acciones = 0
            partida.enemigo.vida = 0
            co = self.capturePrint()
            partida.comprobarEstado()
            # El enemigo ha muerto y no ha atacado
            self.assertEqual(partida.enemigo, None)
            self.assertFalse(partida.peligro)
            self.assertTrue("ha sido justamente purgado." in co.getvalue())
            self.assertFalse("TURNO DEL ENEMIGO" in co.getvalue())
            self.assertEqual(jugador.acciones, jugador.accionesBase)

            # Sin peligro
            partida.activa = True
            jugador.vida = jugador.maxVida
            jugador.acciones = 0
            co = self.capturePrint()
            partida.comprobarEstado()
            self.assertTrue("El tiempo corre en su contra. "
                            "Falto de opciones, el Aniquilador se mueve." in co.getvalue())
            self.assertTrue("\nEntras a una NUEVA SALA." in co.getvalue())
            # Recupera las acciones
            if "¡Desastre!" in co.getvalue():
                self.assertEqual(jugador.acciones, 0)
            else:
                self.assertEqual(jugador.acciones, jugador.accionesBase)

            # Jugador sin vida
            self.assertTrue(partida.activa)

            # Destruido por el enemigo
            partida.crearEnemigo()
            jugador.acciones = 0
            jugador.vida = 0  # Nos aseguramos que aunque falle los ataques, muera
            co = self.capturePrint()
            partida.comprobarEstado()
            self.assertTrue("\nEl Aniquilador {} ha sido exterminado por los alienígenas.".format(
                jugador.nombre
            ) in co.getvalue())
            self.assertFalse(partida.activa)

            # Destruido por las circunstancias
            partida.activa = True
            partida.destruirEnemigo()
            jugador.vida = 1
            jugador.acciones = jugador.accionesBase
            partida.desastre()
            co = self.capturePrint()
            partida.comprobarEstado()
            self.assertTrue("\nEl Aniquilador {} ha sido exterminado por los alienígenas.".format(
                jugador.nombre
            ) in co.getvalue())
            self.assertFalse(partida.activa)

            # Al sr obligado a entrar en una nueva sala por agotar las acciones

            partida.activa = True
            while "¡Desastre!" not in co.getvalue():
                partida.destruirEnemigo()
                jugador.acciones = 0
                jugador.vida = 1
                co = self.capturePrint()
                partida.comprobarEstado()
            self.assertTrue("\nEl Aniquilador {} ha sido exterminado por los alienígenas.".format(
                jugador.nombre
            ) in co.getvalue())


if __name__ == '__main__':
    unittest.main()
