import sys

from lexer import lexer, tokprint_code, tokprint_table
from parser import parser, filecontent
from generator import CodeGenerator
from emitter import CodeEmitter

def test_lexer(input_string):
    lexer.input(input_string)
    while tok := lexer.token():
        print(f"Token: {tok.type:<15} Valor: {tok.value}")

def test_parser(input_string):
    r = parser.parse(input_string)
    return r

def main():
    with open(sys.argv[1]) as input_file:
        text = input_file.read()

        # test_lexer(text)
        ast = test_parser(text)
        print(" _")
        print(ast)

        # restart lexer to print tokens
        # lexer = lex.lex()
        # lexer.input(text)
        # tokens = list(lexer)
        # tokprint_code(tokens)
        # print()
        # tokprint_table(tokens)
        # print()

        # generate code
        em = CodeEmitter()
        gen = CodeGenerator(em)
        gen.generate(ast)
        compiled = em.dump()
        with open(f"{gen.program_name}.out", "w") as output_file:
            output_file.write(compiled)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Argumentos insuficientes")
        print("Uso correto: python3 main.py <ficheiro_de_entrada>")
        exit(1)

    main()
