def leer_gramaticas(archivo):
    with open(archivo, 'r') as f:
        lineas = f.read().splitlines()

    numero_gramaticas = int(lineas[0])
    indice = 1
    gramaticas = []

    for _ in range(numero_gramaticas):
        num_no_terminales = int(lineas[indice])
        indice += 1

        producciones = {}
        for _ in range(num_no_terminales):
            izquierda, *derechas = lineas[indice].split()
            if izquierda not in producciones:
                producciones[izquierda] = []
            producciones[izquierda].extend(derechas)
            indice += 1

        gramaticas.append(producciones)

    return gramaticas

# Función para calcular FIRST
def calcular_first(producciones):
    first = {nt: set() for nt in producciones}

    def obtener_first(no_terminal, visitados):
        if no_terminal in first and first[no_terminal]:
            return first[no_terminal]

        if no_terminal in visitados:
            return set()  # Evita recursión infinita en ciclos

        visitados.add(no_terminal)
        primeros = set()

        for produccion in producciones.get(no_terminal, []):
            if produccion == 'e':
                primeros.add('e')
                continue

            for simbolo in produccion:
                if simbolo.islower():  # Es un terminal
                    primeros.add(simbolo)
                    break
                else:  # Es un no terminal
                    simbolo_first = obtener_first(simbolo, visitados)
                    primeros.update(simbolo_first - {'e'})
                    if 'e' not in simbolo_first:
                        break
            else:
                primeros.add('e')

        visitados.remove(no_terminal)
        first[no_terminal] = primeros
        return primeros

    for no_terminal in producciones:
        obtener_first(no_terminal, set())

    return first

# Función para calcular FOLLOW
def calcular_follow(producciones, first):
    simbolo_inicial = next(iter(producciones))
    follow = {nt: set() for nt in producciones}
    follow[simbolo_inicial].add('$')  # Añadir $ al FOLLOW del símbolo inicial

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, reglas in producciones.items():
            for produccion in reglas:
                for i, simbolo in enumerate(produccion):
                    if simbolo.isupper():  # Solo procesamos no terminales
                        siguiente = produccion[i + 1:]
                        if siguiente:
                            if siguiente[0].islower():
                                if siguiente[0] not in follow[simbolo]:
                                    follow[simbolo].add(siguiente[0])
                                    cambio = True
                            else:
                                first_siguiente = first[siguiente[0]] - {'e'}
                                if not first_siguiente.issubset(follow[simbolo]):
                                    follow[simbolo].update(first_siguiente)
                                    cambio = True
                                if 'e' in first[siguiente[0]]:
                                    if not follow[no_terminal].issubset(follow[simbolo]):
                                        follow[simbolo].update(follow[no_terminal])
                                        cambio = True
                        else:
                            if not follow[no_terminal].issubset(follow[simbolo]):
                                follow[simbolo].update(follow[no_terminal])
                                cambio = True

    return follow

# Código principal para ejecutar la gramática y analizar cadenas
archivo = 'input.txt'
gramaticas = leer_gramaticas(archivo)

for i, producciones in enumerate(gramaticas):
    print(f"\nGramática {i + 1}:")
    for no_terminal, reglas in producciones.items():
        print(f"{no_terminal} -> {' | '.join(reglas)}")

    first = calcular_first(producciones)
    follow = calcular_follow(producciones, first)

    print("\nConjunto FIRST:")
    for nt, primeros in first.items():
        print(f"FIRST({nt}) = {{ {', '.join(primeros)} }}")

    print("\nConjunto FOLLOW:")
    for nt, segundos in follow.items():
        print(f"FOLLOW({nt}) = {{ {', '.join(segundos)} }}")

