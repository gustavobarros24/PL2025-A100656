# Analisador Léxico

## 2025-xx-xx

## Autor:

- A100656
- Gustavo Manuel Marinho Barros

## Enunciado:

Construir um analisador léxico para uma liguagem de query com a qual se podem escrever frases do género:

## Exemplo:

DBPedia: obras de Chuck Berry
    select ?nome ?desc where {
        ?s a dbo:MusicalArtist.
        ?s foaf:name "Chuck Berry"@en .
        ?w dbo:artist ?s.
        ?w foaf:name ?nome.
        ?w dbo:abstract ?desc
    } LIMIT 1000

## Resumo:
