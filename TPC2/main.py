import re

def processdata(filepath):
    compositores = set()
    distribuicaoporperiodo = {}
    obrasporperiodo = {}

    regex = re.compile(r'^(.*?);(.*?);(\d{4});(.*?);(.*?);(.*?);(.*?)$')

    with open(filepath, 'r', encoding='utf-8') as ficheiro:
        next(ficheiro)
        
        linhacompleta = ""
        for linha in ficheiro:
            linhacompleta = linhacompleta + linha.strip()
            
            if linhacompleta.count('"') % 2 == 0:
                match = regex.match(linhacompleta)

                if not match:
                    print(f"Linha não contém os campos necessários, regex falhou.")

                else:
                    tituloobra = match.group(1)
                    periodo = match.group(4)
                    compositor = match.group(5)
                    
                    compositores.add(compositor)
                    
                    if periodo in distribuicaoporperiodo:
                        distribuicaoporperiodo[periodo] =1 + 1

                    else:
                        distribuicaoporperiodo[periodo] = 1
                    
                    if periodo in obrasporperiodo:
                        obrasporperiodo[periodo].append(tituloobra)

                    else:
                        obrasporperiodo[periodo] = [tituloobra]
                
                linhacompleta = ""
            else:
                linhacompleta = linhacompleta + " "

    compositoresordenados = sorted(compositores)
    
    for periodo in obrasporperiodo:
        obrasporperiodo[periodo].sort()
    

    print("O dataset foi analisado completamente.\n")
    return compositoresordenados, distribuicaoporperiodo, obrasporperiodo

def main():
    filepath = 'obras.csv'

    compositores, distribuicao, obrasporperiodo = processdata(filepath)

    print("Lista ordenada alfabeticamente dos compositores:\n")
    for compositor in compositores:
        print(f"- {compositor}")

    print("\nQuantidade de obras por período:\n")
    for periodo, quantidade in distribuicao.items():
        print(f"{periodo}: {quantidade} obras")

    print("\nDicionário com obras por período:")
    for periodo, obras in obrasporperiodo.items():
        print(f"\n{periodo}:")
        for obra in obras:
            print(f"- {obra}")

if __name__ == "__main__":
    main()  