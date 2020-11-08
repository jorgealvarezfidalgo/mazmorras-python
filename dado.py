from random import randint


'''Este módulo se encarga de simular el funcionamiento de un dado.'''


'''Tirada entre 1 y 100 (1D100)'''
def und100():
    return randint(1, 100)


'''Tirada entre 1 y 6 (1D6)'''
def und6():
    return randint(1, 6)


'''Tirada entre 1 y 3 (1D3)'''
def und3():
    return randint(1, 3)


'''Tirada entre 1 y 2 (1D2)'''
def und2():
    return randint(1, 2)


'''Devuelve un 3 (resultado fijo)'''
def d3():
    return 3


'''Devuelve un 2 (resultado fijo)'''
def d2():
    return 2


'''Devuelve un 1 (resultado fijo)'''
def tirada_minima():
    return 1


'''Un formato más cuidado para cada tipo de tirada, de cara a mostrar en las descripciones de armas.'''
tiradas_dado = {
    'und6': 'D6',
    'und3': 'D3',
    'und2': 'D2',
    'd3': '3',
    'd2': '2',
    'tirada_minima': '1',
}
