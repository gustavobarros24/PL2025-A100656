import ply.yacc as yacc
from tpc6_lex import tokens
import sys


def p_global(p):
    """
    S : Exp
    """
    print(f"Valor da expressão: {p[1]}")
    p[0] = p[1]

def p_exp_add(p):
    """
    Exp : Exp ADD Exp
    """
    p[0] = p[1] + p[3]

def p_exp_sub(p):
    """
    Exp : Exp SUB Exp
    """
    p[0] = p[1] - p[3]

def p_exp_mul(p):
    """
    Exp : Exp MUL Exp
    """
    p[0] = p[1] * p[3]

def p_exp_num(p):
    """
    Exp : NUM
    """
    p[0] = int(p[1])

def p_exp_paren(p):
    """
    Exp : PA Exp PF
    """
    p[0] = p[2]

def p_error(p):
    print('Erro sintático: ', p)
    parser.success = False

parser = yacc.yacc()

def main():
    for linha in sys.stdin:
        parser.success = True
        parser.parse(linha)
        if parser.success:
            print("Frase válida: ", linha)
        else:
            print("Frase inválido... Corrija e tente novamente!")

if __name__ == "__main__":
    main()