import ply.lex as lex
import re


tokens = (
    'IDENTIFIER',    # ex: dbo:MusicalArtist, foaf:name
    'PREFIX',        # ex: DBPedia:
    'SELECT',        # select
    'WHERE',         # where
    'LIMIT',         # LIMIT
    'VAR',           # variáveis como ?nome, ?desc
    'STRING',        # strings como "Chuck Berry"@en
    'NUMBER',        # números como 1000
    'LBRACE',        # {
    'RBRACE',        # }
    'DOT',           # .
    'AT',            # @
    'TEXT'           # Texto livre
)

t_PREFIX = r'[A-Za-z]+:'
t_SELECT = r'select'
t_WHERE = r'where'
t_LIMIT = r'LIMIT'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_DOT = r'\.'
t_AT = r'@'

def t_VAR(t):
    r'\?[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_STRING(t):
    r'"[^"]*"@[a-z]+|"[^"]*"'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_TEXT(t):
    r'[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*'
    return t

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

def analyze_query(query):
    lexer.input(query)
    while True:
        tok = lexer.token()

        if not tok:
            break

        print(f"Token: {tok.type}, Valor: {tok.value}, Linha: {tok.lineno}")

def main():
    query = """
    DBPedia: obras de Chuck Berry
        select ?nome ?desc where {
            ?s a dbo:MusicalArtist.
            ?s foaf:name "Chuck Berry"@en .
            ?w dbo:artist ?s.
            ?w foaf:name ?nome.
            ?w dbo:abstract ?desc
        } LIMIT 1000
    """
    print("Analisando a query:")
    analyze_query(query)

if __name__ == "__main__":
    main()