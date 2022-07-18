def rule(sequence, rules):
    """
    Searches in the given sequence for chars at which the rules shoud be applied, if found apploes rule
    :param sequence: sequence to search in
    :param rules: set of rules
    :return: the new sequence with applied rules
    """
    """ Searches in given <sequence> for the rule to replace """
    if sequence in rules:
        return rules[sequence]
    return sequence


def derivation(derived, steps, rules):
    """
    For each step applies rule to the sequence appends them to the sequence before and appends this to the list of derived,
    :param derived: should be a list which at least one element where to start the derivation of rules
    :param steps: how much times the derivations should be applied
    :param rules: rules to use for derivation
    :return: list of derivations
    """
    for _ in range(steps):
        next_seq = derived[-1]
        # Für jeden <char> in <next_seq> prüfe, ob die Regel angewendet werden muss
        next_axiom = [rule(char, rules) for char in next_seq]
        derived.append(''.join(next_axiom))
    return derived


def splitRule(input):
    """
    Splits rule string by searching for '=' and creating dictionary with key left from it and value right from it
    :param input: string input to get rule from
    :return: dictionary with rule
    """
    x = input.split('=', 1)
    return {x[0]: x[1]}