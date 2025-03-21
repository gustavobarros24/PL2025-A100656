# Recursivo Descendente para expressões aritméticas

## 2025-03-21

## Autor:

- A100656
- Gustavo Manuel Marinho Barros

## Enunciado:

Baseado nos materiais fornecidos na aula, cria um parser LL(1) recursivo descendente que reconheça expressões aritméticas e calcule o respetivo valor.

## Exemplo:

2+3
67-(2+3*4)
(9-2)*(13-4)


## Resumo:

É feito um analisador léxico para tokenizar as strings dos inputs através do alfabeto apresentado.
Noutro ficheiro foi feita a gramática e usado o ply.yacc para o parser.