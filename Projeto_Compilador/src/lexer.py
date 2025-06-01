from ply import lex
import sys

keyword_tokens = (
    'IF', 'THEN', 'ELSE',

    'FOR', 'WHILE', 'REPEAT', 'UNTIL', 'DO', 'TO', 'DOWNTO', 'OF',
	
    'VAR', 'CONST', 'BEGIN', 'END',
	
    'PROGRAM', 'PROCEDURE', 'FUNCTION', 'ARRAY', 'RETURN',
)

datatype_tokens = (
    'TYPEBOOL',   'FALSE', 'TRUE',
    'TYPEREAL',	  'REALVALUE',
    'TYPEINT',    'INTVALUE',
    'TYPESTRING', 'STRINGVALUE',
    'TYPECHAR',   'CHARVALUE'
)

punctuation_tokens = (
    'DOTDOT', 'DOT', 'SEMICOLON', 'COLON', 'COMMA',

	'LPAREN', 'RPAREN', 'LSPAREN', 'RSPAREN', #'LBRACE', 'RBRACE',
)

operator_tokens = (
    'ASSIGN',

    # pascal uses '/' for real division and DIV for int division
	'PLUS', 'MINUS', 'TIMES', 'REALDIV', 'INTDIV', 'MOD', 
	
    'AND', 'OR', 'NOT',

    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
)

tokens = keyword_tokens + punctuation_tokens + operator_tokens + datatype_tokens + (
    'IDENTIFIER', #'SLASHCOMMENT', 'BRACECOMMENT', 'PARENCOMMENT'
)


def t_BRACECOMMENT(t): r'\{[^}]*\}';         t.lexer.lineno += t.value.count('\n'); pass
def t_PARENCOMMENT(t): r'\(\*[.\s\S]*?\*\)'; t.lexer.lineno += t.value.count('\n'); pass
def t_SLASHCOMMENT(t): r'\/\/.*?\n';         t.lexer.lineno += 1; pass

def t_PROCEDURE(t):  r'[pP][rR][oO][cC][eE][dD][uU][rR][eE]'; return t
def t_FUNCTION(t):   r'[fF][uU][nN][cC][tT][iI][oO][nN]'; return t
def t_TYPEBOOL(t):   r'[bB][oO][oO][lL][eE][aA][nN]'; return t
def t_PROGRAM(t):    r'[pP][rR][oO][gG][rR][aA][mM]'; return t
def t_TYPEINT(t):    r'[iI][nN][tT][eE][gG][eE][rR]'; return t 
def t_RETURN(t):     r'[rR][eE][tT][uU][rR][nN]'; return t
def t_REPEAT(t):     r'[rR][eE][pP][eE][aA][tT]'; return t
def t_DOWNTO(t):     r'[dD][oO][wW][nN][tT][oO]'; return t
def t_TYPESTRING(t): r'[sS][tT][rR][iI][nN][gG]'; return t
def t_WHILE(t):      r'[wW][hH][iI][lL][eE]'; return t
def t_UNTIL(t):      r'[uU][nN][tT][iI][lL]'; return t
def t_CONST(t):      r'[cC][oO][nN][sS][tT]'; return t
def t_BEGIN(t):      r'[bB][eE][gG][iI][nN]'; return t
def t_FALSE(t):      r'[fF][aA][lL][sS][eE]'; return t
def t_ARRAY(t):      r'[aA][rR][rR][aA][yY]'; return t
def t_TYPEREAL(t):   r'[rR][eE][aA][lL]'; return t
def t_TYPECHAR(t):   r'[cC][hH][aA][rR]'; return t
def t_THEN(t):       r'[tT][hH][eE][nN]'; return t
def t_TRUE(t):       r'[tT][rR][uU][eE]'; return t
def t_ELSE(t):       r'[eE][lL][sS][eE]'; return t
def t_VAR(t):        r'[vV][aA][rR]'; return t
def t_AND(t):        r'[aA][nN][dD]'; return t
def t_FOR(t):        r'[fF][oO][rR]'; return t
def t_END(t):        r'[eE][nN][dD]'; return t
def t_NOT(t):        r'[nN][oO][tT]'; return t
def t_MOD(t):        r'[mM][oO][dD]'; return t
def t_INTDIV(t):     r'[dD][iI][vV]'; return t
def t_DO(t):         r'[dD][oO]'; return t
def t_IF(t):         r'[iI][fF]'; return t
def t_TO(t):         r'[tT][oO]'; return t
def t_OR(t):         r'[oO][rR]'; return t
def t_OF(t):         r'[oO][fF]'; return t
def t_DOTDOT(t):     r'\.\.'; return t
def t_NEQ(t):        r'\<\>'; return t
def t_LTE(t):        r'\<\='; return t
def t_GTE(t):        r'\>\='; return t
def t_ASSIGN(t):     r'\:\='; return t
def t_DOT(t):        r'\.'; return t
def t_SEMICOLON(t):  r'\;'; return t
def t_COLON(t):      r'\:'; return t
def t_COMMA(t):      r'\,'; return t
def t_LPAREN(t):     r'\('; return t
def t_RPAREN(t):     r'\)'; return t
def t_LSPAREN(t):    r'\['; return t
def t_RSPAREN(t):    r'\]'; return t
# def t_LBRACE (t):    r'\{'; return t
# def t_RBRACE (t):    r'\}'; return t
def t_PLUS(t):       r'\+'; return t
def t_MINUS (t):     r'\-'; return t
def t_TIMES (t):     r'\*'; return t
def t_REALDIV(t):    r'\/'; return t
def t_EQ(t):         r'\='; return t
def t_LT(t):         r'\<'; return t
def t_GT(t):         r'\>'; return t

def t_REALVALUE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTVALUE(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CHARVALUE(t):
    r"'([^']{1})'"
    t.value = t.value[1:-1]
    return t

def t_STRINGVALUE(t):
    r"'([^']*)'"
    t.value = t.value[1:-1]
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_\$][a-zA-Z_0-9\$]*'
    t.value = t.value.lower()
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"[Ln {t.lineno}] Lexical Error: \'{t.value[0]}\'")
    # t.lexer.skip(1)
    exit(1)

lexer = lex.lex()

def tokprint_table(tokens):
    print("{:<10} {:<10} {:<15} {:<20}".format("Line", "Pos", "Type", "Value",))
    print("-" * 50)
    for tok in tokens:
        print("{:<10} {:<10} {:<15} {:<20}".format(
            tok.lineno, 
            tok.lexpos,
            tok.type, 
            str(tok.value), 
        ))

def tokprint_code(tokens):
    current_line = 1
    print(f"{current_line:4d}: ", end="")
    for tok in tokens:
        while tok.lineno > current_line:
            current_line += 1
            print(f"\n{current_line:4d}: ", end="")
        print(f"{tok.value} ", end="")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Argumentos insuficientes")
        exit(1)
        
    filecontent = ""

    with open(sys.argv[1], encoding='utf-8') as input_file:
        filecontent = input_file.read()
        lexer = lex.lex()
        lexer.input(filecontent)
        tokens = list(lexer)
        tokprint_code(tokens)
        print()
        tokprint_table(tokens)
        print()