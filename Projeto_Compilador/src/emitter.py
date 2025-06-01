class CodeEmitter:
    def __init__(self):
        self.code = []
        self.label_count = 0
        self.temp_count = 0
    
    def new_label(self, base="L"):
        new_label = f"{base}{self.label_count}"
        self.label_count += 1
        return new_label

    def emit(self, instruction: str):
        self.code.append(instruction)
    
    def dump(self):
        return "\n".join(self.code)
