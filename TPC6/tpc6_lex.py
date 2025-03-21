import ply.lex as lex


tokens = (
    'NUM',
    'ADD',
    'SUB',
    'MUL',
    'PA',
    'PF'
)

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_PA = r'\('
t_PF = r'\)'
t_NUM = r'\d+'
t_ignore = '\t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()