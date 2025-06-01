
class Node:
    def __init__(self, label, *args):
        self.label = label
        self.args: list[Node] = list(args)
    
    def add_child(self, node):
        self.args.append(node)

    def _strOG(self, prefix="", is_last=True):
        # Define o conector visual de acordo com se é o último filho ou não
        connector = "└── " if is_last else "├── "

        result = prefix + connector + str(self.label) + "\n"

        # Atualiza o prefixo para os filhos; se é o último, não imprime a linha vertical
        new_prefix = prefix + ("    " if is_last else "│   ")

        child_count = len(self.args)
        for idx, arg in enumerate(self.args):
            is_child_last = (idx == (child_count - 1))

            if isinstance(arg, Node):
                result += arg._str(new_prefix, is_child_last)
            else:
                result += new_prefix + ("└── " if is_child_last else "├── ") + str(arg) + "\n"

        return result
    
    def _str(self, prefix="", is_last=True):
        RULE_COLOR  = '\033[3m\033[94m' # Italic + Blue
        TOKEN_COLOR = '\033[92m'        # Green
        RESET_COLOR = '\033[0m'
        
        rule = lambda str: f"{RULE_COLOR}{str}{RESET_COLOR}"
        tok = lambda str: f"{TOKEN_COLOR}{str}{RESET_COLOR}"

        # Define o conector visual de acordo com se é o último filho ou não
        connector = " └──" if is_last else " ├──"
        colored_label = tok(self.label) if self.label.isupper() else rule(self.label)
        
        result = f"{prefix}{connector}<{colored_label}>\n"

        # Atualiza o prefixo para os filhos; se é o último, não imprime a linha vertical
        new_prefix = prefix + ("     " if is_last else " │   ")

        child_count = len(self.args)
        for idx, arg in enumerate(self.args):
            is_child_last = (idx == (child_count - 1))
            
            if isinstance(arg, Node):
                result += arg._str(new_prefix, is_child_last)
            else:
                value = str(arg)
                child_connector = " └──" if is_child_last else " ├──"
                result += f"{new_prefix}{child_connector}\"{value}\"\n"

        return result

    def __str__(self):
        return self._str()
