import re

def markdowntohtml(markdowntext):
    def processinline(text):
        text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1"/>', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        return text

    lines = markdowntext.split('\n')
    htmllines = []
    inorderedlist = False

    for line in lines:
        line = line.strip()

        if not line:
            if inorderedlist:
                htmllines.append('</ol>')
                inorderedlist = False
            htmllines.append('')
            continue

        if line.startswith('# '):
            htmllines.append(f'<h1>{processinline(line[2:])}</h1>')
        elif line.startswith('## '):
            htmllines.append(f'<h2>{processinline(line[3:])}</h2>')
        elif line.startswith('### '):
            htmllines.append(f'<h3>{processinline(line[4:])}</h3>')
        elif re.match(r'^\d+\.\s', line):
            if not inorderedlist:
                htmllines.append('<ol>')
                inorderedlist = True
            itemtext = re.sub(r'^\d+\.\s', '', line)
            htmllines.append(f'    <li>{processinline(itemtext)}</li>')
        else:
            if inorderedlist:
                htmllines.append('</ol>')
                inorderedlist = False
            htmllines.append(processinline(line))

    if inorderedlist:
        htmllines.append('</ol>')

    return '\n'.join(htmllines)

def main():
    testmarkdown = """# Exemplo
    Este é um **exemplo** com *itálico* e [link](http://www.google.pt)
    ## Segundo nível
    1. Primeiro item
    2. Segundo **item** com ![imagem](google.jpg)
    3. Terceiro item
    Texto normal depois da lista"""

    htmloutput = markdowntohtml(testmarkdown)
    print("Markdown de entrada:")
    print(testmarkdown)
    print("\nHTML de saída:")
    print(htmloutput)

    #User input
    print("\nDigite seu próprio texto Markdown (ou pressione Enter para sair):")
    userinput = input()
    if userinput:
        userhtml = markdowntohtml(userinput)
        print("\nSeu HTML:")
        print(userhtml)

if __name__ == "__main__":
    main()