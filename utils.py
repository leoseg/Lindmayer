def rule(sequence, rules):
    """ Sucht in der gegebenen <sequence> nach der entsprechend zu ersetztenden Regel """
    if sequence in rules:
        return rules[sequence]
    return sequence


def derivation(derived, steps, rules):
    """ Erzeugt mit der Regel für jeden Iterationsschritt einen Sequenz an Zeichenbefehlen """
    for _ in range(steps):
        next_seq = derived[-1]
        # Für jeden <char> in <next_seq> prüfe, ob die Regel angewendet werden muss
        next_axiom = [rule(char, rules) for char in next_seq]
        derived.append(''.join(next_axiom))
    return derived


def splitRule(input):
    """input muss "=" enthalten, z.B. "F=FF+[+F-F-F]-[-F+F+F]". F ist der Pattern der mit FF+[+F-F-F]-[-F+F+F] ersetzt wird"""
    x = input.split('=', 1)
    return {x[0]: x[1]}