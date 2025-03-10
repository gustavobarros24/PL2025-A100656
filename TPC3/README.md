# Conversor de MarkDown para HTML

## 2025-03-09

## Autor:

- A100656
- Gustavo Manuel Marinho Barros

## Enunciado:

Criar em Python um pequeno conversor de MarkDown para HTML para os elementos descritos na "Basic Syntax" da Cheat Sheet:

Cabeçalhos: linhas iniciadas por "# texto", ou "## texto" ou "### texto"

Bold: pedaços de texto entre "**"

Itálico: pedaços de texto entre "*"

Lista numerada

Link: "[texto](endereço URL)"

Imagem: "![texto alternativo](path para a imagem)"

## Resumo:

O texto Markdown dado é processado linha por linha, nas quais identifica e converte a sintaxe Markdown em (tags) HTML.

O processo é dividido em duas etapas:

1: Utiliza expressões regulares para identificar e substituir Markdown pelas tags equivalentes em HTML.

2: Em cada linha do texto identifica cabeçalhos (#, ##, ###) e listas numeradas, convertendo-os para <h1>, <h2>, <h3> e <ol> com <li>, respectivamente.

No fim junta tudo numa string e separa tudo com /n (return '\n'.join(htmllines))

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