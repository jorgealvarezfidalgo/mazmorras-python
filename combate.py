import dado

'''Todas aquellas funciones relativas a la resolución del combate'''

'''
Determina si un ataque hiere a partir de la proporción entre capacidad de herir del arma y resistencia
del objetivo.
'''
def hiere(her, res):
    return x_o_mas(calcular_prop(her, res))


'''
Calcula la proporción entre capacidad de herir y resistencia del objetivo para indicar el mínimo necesario
a obtener en la tirada. Por lo general, cuanto mayor el herir frente a la resistencia, más sencillo.
'''
def calcular_prop(her, res):
    p = her / res
    if p == 1:
        return 4
    elif p <= 0.5:
        return 6
    elif p >= 2:
        return 2
    elif p < 1:
        return 5
    elif p > 1:
        return 3


'''
Determina si una tirada es exitosa, dado el límite.
Un valor de 3 representa una tirada de 3+: triunfa con 3 o más.
'''
def x_o_mas(x):
    return dado.und6() >= x


'''
Determina si la tirada de salvación es exitosa a partir de la salvación base y con el modificador de penetración.
'''
def salva(sv, ap):
    return x_o_mas(sv - ap)


'''
Se calcula el ataque de un arma a un objetivo.
1. Se comprueba que hay objetivo.
2. Si existe, se ejecuta el efecto especial del arma sobre el objetivo.
3. Se realiza la tirada para impactar.
4. Se realiza la tirada para herir.
5. Se realiza la tirada de salvación. Si esta falla, el objetivo recibe el daño del arma.
'''
def resolver_ataque(atacante, objetivo):
    if objetivo is None:
        print("En un arrebato de furia, atacas el mobiliario de la sala. Un acto que no provee de mayor"
              " gloria al CENSURADO PARA DESCLASIFICACIÓN.")
        return False
    if atacante.efectoact:
        atacante.efectoact(objetivo)
    '''Impactar'''
    if not x_o_mas(atacante.impacto):
        print("No se ha conseguido impactar al {}.".format(type(objetivo).__name__))
        return False
    if not hiere(atacante.herir, objetivo.resistencia):
        print("No se ha conseguido herir al {}.".format(type(objetivo).__name__))
        return False
    print("Se ha impactado y herido al {}.".format(type(objetivo).__name__))
    if not salva(objetivo.save, atacante.ap):
        dmg = objetivo.reducirSalud(atacante.damage)  # Duck Typing, puede ser Exterminador o Tiránido
        print("El {} recibe {} heridas.".format(type(objetivo).__name__, dmg))
        return True
    print("El {} regenera sus tejidos celulares y salva sus heridas.".format(type(objetivo).__name__))


'''
Recibe una función parcial (mod) y la ejecuta para cada uno de los atributos (ats) del objetivo.
'''
def aplicar_efecto(obj, mod, ats):
    for at in ats:
        exec("obj.{} = mod(obj.{})".format(at, at))
