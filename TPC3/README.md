# Conversor de MarkDown para HTML

## 2025-xx-xx

## Autor:

- A100656
- Gustavo Manuel Marinho Barros

## Enunciado:

Criar em Python um pequeno conversor de MarkDown para HTML para os elementos descritos na "Basic
Syntax" da Cheat Sheet:

Cabeçalhos: linhas iniciadas por "# texto", ou "## texto" ou "### texto"

Bold: pedaços de texto entre "**"

Itálico: pedaços de texto entre "*"

Lista numerada

Link: "[texto](endereço URL)"

Imagem: "![texto alternativo](path para a imagem)"

## Resumo:


## Exemplo:

In: # Exemplo
Out: <h1>Exemplo</h1>

In: Este é um exemplo ...
Out: Este é um <b>exemplo</b> ...

In: Este é um exemplo ...
Out: Este é um <i>exemplo</i> ...

In: 1. Primeiro item
    2. Segundo item
    3. Terceiro item
Out:
    <ol>
    <li>Primeiro item</li>
    <li>Segundo item</li>
    <li>Terceiro item</li>
    </ol>

In: Como pode ser consultado em página da UC
Out: Como pode ser consultado em <a href="http://www.uc.pt">página da UC</a>

In:  Como se vê na imagem seguinte: imagem dum coelho ...
Out: Como se vê na imagem seguinte: <img src="http://www.coellho.com" alt="imagem
dum coelho"/> ...