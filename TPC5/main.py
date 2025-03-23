import json
import sys
import ply.lex as lex


tokens = [
    'COIN',
    'LIST',
    'SELECT',
    'LEAVE',
    'VALUE',
    'CODE',
    'COMMA'
]

def t_COIN(t):
    r'COIN'
    return t

def t_LIST(t):
    r'LIST'
    return t

def t_SELECT(t):
    r'SELECT'
    return t

def t_LEAVE(t):
    r'LEAVE'
    return t

def t_VALUE(t):
    r'\d+[ec]'
    return t

def t_CODE(t):
    r'[A-Z]\d+'
    return t

def t_COMMA(t):
    r','
    return t

t_ignore = '\t\n'

def t_error(t):
    print(f"[LEXER] Caráter não reconhecido: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

def carregarstock(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O ficheiro {filename} não foi encontrado.")
        sys.exit(1)

def salvarstock(filename, stock):
    with open(filename, 'w') as f:
        json.dump(stock, f, indent=4)

def listarprodutos(stock):
    print("cod    |  nome      |  quantidade  |  preço")
    print("---------------------------------")
    for produto in stock:
        print(f"{produto['cod']: <7} | {produto['nome']: <10} | {produto['quant']: <12} | {produto['preco']:.2f}€")

def processarmoedas(moedas):
    saldo = 0
    for moeda in moedas:
        if moeda.endswith('e'):
            saldo += int(moeda[:-1]) * 100
        elif moeda.endswith('c'):
            saldo += int(moeda[:-1])
    return saldo

def selecionarproduto(codigo, stock, saldo):
    for produto in stock:
        if produto['cod'] == codigo:
            if produto['quant'] > 0:
                preco_centimos = int(produto['preco'] * 100)
                if saldo >= preco_centimos:
                    produto['quant'] -= 1
                    saldo -= preco_centimos
                    print(f'maq: Pode retirar o produto dispensado "{produto["nome"]}"')
                    return saldo
                else:
                    print(f'maq: Saldo insuficiente para satisfazer o seu pedido')
                    print(f'maq: Saldo = {saldo//100}e{saldo%100}c; Pedido = {produto["preco"]:.2f}€')
                    return saldo
            else:
                print(f'maq: O produto "{produto["nome"]}" está esgotado.')
                return saldo
    print(f'maq: O produto com código "{codigo}" não existe.')
    return saldo

def sair(saldo):
    if saldo > 0:
        moedas = []
        for valor in [50, 20, 10, 5, 2, 1]:
            count = saldo // valor
            if count > 0:
                moedas.append(f"{count}x {valor}c")
                saldo -= count * valor
        print(f'maq: Pode retirar o troco: {", ".join(moedas)}.')
    print('maq: Até à próxima')

def main():
    filename = "stock.json"
    stock = carregarstock(filename)
    saldo = 0

    print("maq: Bom dia. Estou disponível para atender o seu pedido.")
    print("maq: 2024-03-08, Stock carregado, Estado atualizado.")

    while True:
        comando = input(">> ").strip()
        lexer.input(comando)

        token = lexer.token()
        if not token:
            continue

        if token.type == 'LIST':
            listarprodutos(stock)
        elif token.type == 'COIN':
            moedas = []
            while True:
                token_moeda = lexer.token()
                if not token_moeda:
                    break
                if token_moeda.type == 'VALUE':
                    moedas.append(token_moeda.value)
                elif token_moeda.type == 'COMMA':
                    continue
                else:
                    print(f"maq: Formato inválido: '{token_moeda.value}'")
                    break
            saldo += processarmoedas(moedas)
            print(f'maq: Saldo = {saldo//100}e{saldo%100}c')
        elif token.type == 'SELECT':
            token_codigo = lexer.token()
            if token_codigo and token_codigo.type == 'CODE':
                saldo = selecionarproduto(token_codigo.value, stock, saldo)
                print("Saldo atualizado: ", saldo)
            else:
                print("maq: Código de produto inválido.")
        elif token.type == 'LEAVE':
            sair(saldo)
            salvarstock(filename, stock)
            sys.exit(0)
        else:
            print("maq: Comando não reconhecido.")

if __name__ == "__main__":
    main()