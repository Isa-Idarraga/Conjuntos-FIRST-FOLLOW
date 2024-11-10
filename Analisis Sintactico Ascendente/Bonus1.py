import pandas as pd


def read_grammar(file_path):
    """Lee la gramática desde un archivo y la devuelve en forma de diccionario."""
    grammar = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            lhs, rhs = line.strip().split("->")
            lhs = lhs.strip()
            productions = [tuple(prod.strip().split()) for prod in rhs.split('|')]
            grammar[lhs] = productions
    return grammar


def closure(I, grammar):
    """Calcula el CLOSURE de un conjunto de items."""
    closure_set = set(I)
    added = True
    while added:
        added = False
        for item in list(closure_set):
            lhs, rhs, dot_pos = item
            if dot_pos < len(rhs):
                symbol = rhs[dot_pos]
                if symbol in grammar:
                    for production in grammar[symbol]:
                        new_item = (symbol, production, 0)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            added = True
    return closure_set


def goto(I, X, grammar):
    """Calcula la función GOTO."""
    goto_set = set()
    for item in I:
        lhs, rhs, dot_pos = item
        if dot_pos < len(rhs) and rhs[dot_pos] == X:
            goto_set.add((lhs, rhs, dot_pos + 1))
    return closure(goto_set, grammar)


def canonical_lr0_collection(grammar):
    """Construye la colección canónica de items LR(0)."""
    start_symbol = list(grammar.keys())[0] + "'"
    grammar[start_symbol] = [(list(grammar.keys())[0],)]
    initial_item = (start_symbol, grammar[start_symbol][0], 0)

    C = [closure({initial_item}, grammar)]
    added = True

    while added:
        added = False
        for I in C:
            for X in {symbol for lhs, rhs, pos in I for symbol in rhs[pos:pos + 1]}:
                goto_I = goto(I, X, grammar)
                if goto_I and goto_I not in C:
                    C.append(goto_I)
                    added = True
    return C


def compute_follow(grammar):
    """Calcula el conjunto FOLLOW para cada no terminal."""
    follow = {key: set() for key in grammar}
    start_symbol = list(grammar.keys())[0]
    follow[start_symbol].add('$')
    changed = True
    while changed:
        changed = False
        for lhs, productions in grammar.items():
            for rhs in productions:
                for i, symbol in enumerate(rhs):
                    if symbol in grammar:
                        rest = rhs[i + 1:]
                        follow_set = {x for x in rest if x not in grammar}
                        if not rest or all(x in grammar for x in rest):
                            follow_set |= follow[lhs]
                        if follow_set - follow[symbol]:
                            follow[symbol].update(follow_set)
                            changed = True
    return follow


def slr_parsing_table(C, grammar):
    """Construye las tablas ACTION y GOTO para el análisis SLR."""
    ACTION = {}
    GOTO = {}
    follow = compute_follow(grammar)

    for i, I in enumerate(C):
        for item in I:
            lhs, rhs, dot_pos = item
            if dot_pos < len(rhs):
                symbol = rhs[dot_pos]
                if symbol.islower() or symbol in {'+', '*', 'id'}:  # Terminal
                    j = next((k for k, J in enumerate(C) if goto(I, symbol, grammar) == J), None)
                    if j is not None:
                        ACTION[(i, symbol)] = ('shift', j)
            elif dot_pos == len(rhs):
                if lhs == list(grammar.keys())[0] + "'":
                    ACTION[(i, '$')] = ('accept',)
                else:
                    for term in follow[lhs]:
                        ACTION[(i, term)] = ('reduce', lhs, rhs)

        for X in grammar:
            j = next((k for k, J in enumerate(C) if goto(I, X, grammar) == J), None)
            if j is not None:
                GOTO[(i, X)] = j

    return ACTION, GOTO


def print_lr0_collection(C):
    """Imprime la colección LR(0) de forma amigable."""
    print("\nColección LR(0):")
    for i, items in enumerate(C):
        print(f"\nI{i}:")
        for item in sorted(items):
            lhs, rhs, dot_pos = item
            # Convertimos todo a tupla para evitar errores de concatenación
            rhs_str = ' '.join(rhs[:dot_pos] + ('·',) + rhs[dot_pos:])
            print(f"  {lhs} -> {rhs_str}")


def print_slr_table(ACTION, GOTO):
    """Imprime la tabla SLR de forma tabular."""
    print("\nTabla de análisis SLR:")

    # Crear un DataFrame para mostrar la tabla ACTION y GOTO
    terminals = sorted(set(k[1] for k in ACTION.keys()))
    non_terminals = sorted(set(k[1] for k in GOTO.keys()))

    action_df = pd.DataFrame('', index=range(len(set(k[0] for k in ACTION.keys()))), columns=terminals + ['$'])
    goto_df = pd.DataFrame('', index=range(len(set(k[0] for k in GOTO.keys()))), columns=non_terminals)

    for (state, symbol), action in ACTION.items():
        action_df.at[state, symbol] = ' '.join(map(str, action))

    for (state, symbol), goto in GOTO.items():
        goto_df.at[state, symbol] = str(goto)

    print("\nACTION Table:")
    print(action_df.fillna(''))

    print("\nGOTO Table:")
    print(goto_df.fillna(''))


def lr_parser(input_string, ACTION, GOTO, grammar):
    """Implementa el análisis LR para la cadena dada."""
    stack = [0]
    input_string += ' $'
    tokens = input_string.split()
    idx = 0

    print("\nAnálisis paso a paso:")
    while True:
        state = stack[-1]
        symbol = tokens[idx]
        action = ACTION.get((state, symbol))

        # Verificar si hay una acción válida para el estado actual y símbolo
        if action is None:
            print(f"Error de sintaxis en el símbolo '{symbol}' en la posición {idx}")
            return False

        if action[0] == 'shift':
            print(f"Shift: {symbol} -> estado {action[1]}")
            stack.append(action[1])
            idx += 1
        elif action[0] == 'reduce':
            lhs, rhs = action[1], action[2]
            print(f"Reducir usando {lhs} -> {' '.join(rhs)}")
            stack = stack[:-len(rhs)]
            state = stack[-1]
            stack.append(GOTO[(state, lhs)])
        elif action[0] == 'accept':
            print("Cadena aceptada")
            return True


def main():
    # Leer la gramática del archivo
    grammar = read_grammar('input.txt')
    print("Gramática cargada:", grammar)

    # 1. Calcular la colección canónica LR(0)
    C = canonical_lr0_collection(grammar)
    print_lr0_collection(C)

    # 2. Construir tabla SLR
    ACTION, GOTO = slr_parsing_table(C, grammar)
    print_slr_table(ACTION, GOTO)

    # 3. Analizar cadena
    input_string = input("\nIntroduce la cadena a analizar: ")
    lr_parser(input_string, ACTION, GOTO, grammar)


if __name__ == "__main__":
    main()
