import sys

def somaonofftexto(texto):
    res = 0
    flagOn = True
    numero = ""
    
    i = 0

    while i < len(texto):
        digito = texto[i]
        
        if digito.isdigit():
            numero = numero + digito #concatenar

        else:
            if numero:
                if flagOn:
                    res = res + int(numero) #somar
                numero = ""
            
            if texto[i:i+2].upper() == "ON":
                flagOn = True
                i += 1

            elif texto[i:i+3].upper() == "OFF":
                flagOn = False
                i += 2

            elif digito == "=":
                if numero and flagOn:
                    res = res + int(numero)
                    numero = ""

                print(res)
        
        i = i + 1
    
    if numero and flagOn:
        res = res + int(numero)
        print(res)
    
    return res

if __name__ == "__main__":
    for linha in sys.stdin:
        soma = str(somaonofftexto(linha.strip()))
        print("Resultado é: " + soma)


#dsadwadadsadaw45adwadsadw2025-02-07sdadaw=OFFdwasfgsdf789dsadwadsad43dwaONdsadw2adsadasON5=

#45+2025+02+07
#>2079
#2079+2+5
#>2086