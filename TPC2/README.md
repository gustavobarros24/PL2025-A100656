# Análise de um dataset de obras musicais

## 2025-02-23

## Autor:

- A100656
- Gustavo Manuel Marinho Barros

## Enunciado:

Neste TPC, é proibido usar o módulo CSV do Python;
Deverás ler o dataset, processá-lo e criar os seguintes resultados:

1: Lista ordenada alfabeticamente dos compositores musicais;

2: Distribuição das obras por período: quantas obras catalogadas em cada período;

3: Dicionário em que a cada período está a associada uma lista alfabética dos títulos das obras
desse período.

## Resumo:

O programa lê de um csv linha a linha a informação necessária para responder ao enunciado, no caso, os compositores, épocas das obras e obras. Após isso armazena-as em diferentes estruturas de dados, no caso de um set para os compositores, que depois ordena alfabeticamente. Um dicionário para as obras por período, em que um período é incrementado sempre que aparece uma obra do mesmo se não é adicionado uma nova instância. Outro dicionário com as obras que pertencem a cada período, em que é feita a correspondência entre obra e período, as obras correspondentes a cada periodo são também ordenadas.
No fim são printadas as três estruturas no terminal.

## Exemplo:

O csv exemplo é o obras.csv e a solução encontra-se no ficheiro solucao.txt