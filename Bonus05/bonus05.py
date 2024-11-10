# Paso 1: Leer la gramática del archivo
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

# Función para calcular el conjunto FIRST de una cadena
def calcular_first_cadena(cadena, first):
    resultado = set()
    for simbolo in cadena:
        if simbolo.islower():  # Es un terminal
            resultado.add(simbolo)
            break
        resultado.update(first[simbolo] - {'e'})  # Excluye épsilon
        if 'e' not in first[simbolo]:
            break
    else:
        resultado.add('e')
    return resultado

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

# Verificar si la gramática es LL(1)
def es_ll1(producciones, first, follow):
    for nt, reglas in producciones.items():
        first_sets = []
        for regla in reglas:
            first_cadena = calcular_first_cadena(regla, first)
            if 'e' in first_cadena:
                first_cadena = (first_cadena - {'e'}) | follow[nt]
            if any(first_cadena & conjunto for conjunto in first_sets):
                return False
            first_sets.append(first_cadena)
    return True



# Función para analizar una cadena

def construir_tabla_analisis(producciones, first, follow):
    if not ll1:
        tabla = {}

        for nt, reglas in producciones.items():
            for regla in reglas:
                first_regla = calcular_first_cadena(regla, first)
                produccion_completa = f"{nt} -> {''.join(regla)}"

            # Para cada símbolo en FIRST(regla), agregar la producción a la tabla
                for terminal in first_regla - {'e'}:
                    if (nt, terminal) not in tabla:
                        tabla[(nt, terminal)] = []
                    tabla[(nt, terminal)].append(produccion_completa)

            # Si FIRST(regla) contiene 'e', agregar la producción a cada terminal en FOLLOW(nt)
                if 'e' in first_regla:
                    for terminal in follow[nt]:
                        if (nt, terminal) not in tabla:
                            tabla[(nt, terminal)] = []
                        tabla[(nt, terminal)].append(produccion_completa)

        return tabla

    if ll1:

        tabla = {}
        for nt, reglas in producciones.items():
            for regla in reglas:
                first_regla = calcular_first_cadena(regla, first)
                produccion_completa = f"{nt} -> {''.join(regla)}"

                # Para cada símbolo en FIRST(regla), agregar la producción a la tabla
                for terminal in first_regla - {'e'}:
                    if (nt, terminal) not in tabla:
                        tabla[(nt, terminal)] = produccion_completa
                    else:
                        raise ValueError(f"Conflicto en la tabla para ({nt}, {terminal})")

                # Si FIRST(regla) contiene 'e', agregar la producción a cada terminal en FOLLOW(nt)
                if 'e' in first_regla:
                    for terminal in follow[nt]:
                        if (nt, terminal) not in tabla:
                            tabla[(nt, terminal)] = produccion_completa
                        else:
                            raise ValueError(f"Conflicto en la tabla para ({nt}, {terminal})")

        return tabla

# Función mejorada para imprimir la tabla de análisis con múltiples producciones en cada celda
def imprimir_tabla_analisis(tabla):
    if not ll1:
        no_terminales = sorted({nt for (nt, _) in tabla.keys()})
        terminales = sorted({t for (_, t) in tabla.keys()})
        ancho_columna = max(10, max(len(", ".join(producciones)) for producciones in tabla.values()))
        formato = f"{{:<12}}|" + " | ".join([f"{{:<{ancho_columna}}}" for _ in terminales])

        encabezado = formato.format("No Terminal", *terminales)
        separador = "-" * len(encabezado)
        print(encabezado)
        print(separador)

        for nt in no_terminales:
            fila = [" | ".join(tabla.get((nt, t), ["-"])) for t in terminales]
            print(formato.format(nt, *fila))
            print(separador)

    if ll1:
        # Identificar no terminales y terminales únicos a partir de la tabla de análisis
        no_terminales = sorted({nt for (nt, _) in tabla.keys()})
        terminales = sorted({t for (_, t) in tabla.keys()})

        # Definir el ancho de cada columna, ajustando según el tamaño de las producciones
        ancho_columna = max(10, max(
            len(", ".join(producciones)) for producciones in tabla.values()))  # Mínimo ancho de 10 caracteres
        formato = f"{{:<12}}|" + " | ".join([f"{{:<{ancho_columna}}}" for _ in terminales])

        # Imprimir encabezado con líneas divisorias
        encabezado = formato.format("No Terminal", *terminales)
        separador = "-" * len(encabezado)
        print(encabezado)
        print(separador)

        # Imprimir cada fila de la tabla para los no terminales con líneas divisorias
        for nt in no_terminales:
            fila = ["".join(tabla.get((nt, t), ["-"])) for t in terminales]
            print(formato.format(nt, *fila))
            print(separador)

# Función mejorada para analizar la cadena con manejo de errores
def analizar_cadena(cadena, tabla, simbolo_inicial):
    # Inicializar la pila con el símbolo inicial y el delimitador $
    pila = ['$']
    pila.append(simbolo_inicial)
    entrada = list(cadena) + ['$']
    coincidencia = ""

    print(f"{'Coincidencia':<12} {'Pila':<30} {'Entrada':<30} Acción")

    while pila:
        tope = pila.pop()
        simbolo = entrada[0] if entrada else ''  # Asegurar que simbolo no sea vacío

        pila_str = ''.join(reversed(pila))  # Invertir la pila para mostrarla correctamente
        entrada_str = ''.join(entrada) if entrada else ""  # Mostrar la entrada correctamente
        print(f"{coincidencia:<12} {pila_str:<30} {entrada_str:<30} ", end="")

        if tope == simbolo == '$':
            print("Aceptar")
            return True
        elif tope == simbolo:
            entrada.pop(0)  # Avanzar en la entrada
            coincidencia += simbolo
            print(f"Coincidir '{simbolo}'")
        elif tope.isupper():  # Si el tope es un no terminal
            if simbolo and (tope, simbolo) in tabla:
                produccion = tabla[(tope, simbolo)]
                _, regla = produccion.split("->")
                regla = regla.strip()

                print(f"Emitir: {produccion}")
                if regla != 'e':  # No apilamos 'e'
                    for simbolo in reversed(regla):
                        pila.append(simbolo)
                    print(f"Apilando: {regla}")
                else:
                    print("Producción épsilon, no se apila nada.")
            else:
                # Mostrar un mensaje de error más claro
                simbolo_error = simbolo if simbolo else "símbolo vacío o incorrecto"
                print(f"Error: No se encontró producción para ({tope}, {simbolo_error})")
                return False
        else:
            simbolo_error = simbolo if simbolo else "símbolo vacío o incorrecto"
            print(f"Error: El tope '{tope}' no coincide con el símbolo de entrada '{simbolo_error}'")
            return False
    return False



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

    ll1 = es_ll1(producciones, first, follow)
    if ll1:
        print("\nLa gramática es LL(1).")
    else:
        print("\nLa gramática NO es LL(1).")

    if ll1:
        tabla = construir_tabla_analisis(producciones, first, follow)
        print("\nTabla de análisis: \n")
        imprimir_tabla_analisis(tabla)
        cadena = input(f"Ingrese una cadena para analizar con la Gramática {i + 1}: ")
        resultado = analizar_cadena(cadena, tabla, list(producciones.keys())[0]) if ll1 else False
        print("Cadena aceptada." if resultado else "Cadena rechazada.")

    if not ll1:
        tabla = construir_tabla_analisis(producciones, first, follow)
        print("la tabla de analisis queda con ambiguedades por lo que no se puede realizar el analisis sintactico predictivo no recursivo")
        print("\nTabla de análisis: \n")
        imprimir_tabla_analisis(tabla)





