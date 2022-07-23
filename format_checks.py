from tkinter.messagebox import showerror


def checkAxiomFormat(axiomStr):
    """
    Checks if the axiom string has the correct format
    :param axiomStr: str with axiom
    :return: true if correct
    """
    if len(axiomStr) == 0:
        showerror('Missing Entry', 'The "Axiom" must not be empty.')
        return False
    elif not axiomStr in ["F", "G", "R", "L"]:
        showerror('Wrong Entry', 'The axiom must be an element from ("F", "G", "R", "L").')
        return False
    else:
        return True


def checkAngleFormat(angleStr):
    """
    Checks if the angle string has the correct format
    :param angleStr: str with angle
    :return: true if correct
    """
    try:
        if not angleStr.count('.') == 1:
            showerror('Wrong Format', 'In "Angle" must be a number with "." (dot). Do not use "," (comma).')
            return False
        elif float(angleStr) < 0.0:
            showerror('Wrong Format', '"Angle" must bigger then 0.')
            return False
        else:
            return True
    except BaseException:
        showerror('Wrong Format', 'In "Angle" must be a number with "." (dot). Do not use "," (comma).')
        return False


def checkIterationFormat(iterationStr):
    """
    Checks if the iteration string has the correct format
    :param iterationStr: str with iteration number
    :return: true if correct
    """
    if not iterationStr.isnumeric():
        showerror('Wrong Format', '"Iteration" must be a positive number.')
        return False
    else:
        return True


def checkRuleFormat(ruleStr):
    """
    Checks if the rule string has the correct format
    :param ruleStr: str with rule
    :return: true if correct
    """
    if ruleStr.count('=') > 1:
        showerror('Wrong Format', '"Rule" must contain only one "=", e.g. "F=FF+[+F-F-F]-[-F+F+F]".')
        return False
    elif len(ruleStr) == 0:
        showerror('Missing Entry', 'The "Rule" must not be empty.')
        return False
    elif not '=' in ruleStr:
        showerror('Wrong Format', '"Rule" must contain "=", e.g. "F=FF+[+F-F-F]-[-F+F+F]".')
        return False
    else:
        return True