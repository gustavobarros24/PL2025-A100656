from tree import Node
from emitter import CodeEmitter
from scope import Scope

class CodeGenerator:
    def __init__(self, emitter: CodeEmitter):
        self.program_name = None
        self.em = emitter
        # self.global_vars = dict()
        # self.global_var_counter = 0
        self.scope = Scope()
        self.builtin_funcs = {
            'writeln': self._gen_writeln,
            'write': self._gen_write,
            'readln': self._gen_readln,
            'length': self._gen_length,
        }
        self.declared_funcs = dict()


    def generate(self, node: Node):
        method = getattr(self, f"gen_{node.label}", self.not_implemented)
        return method(node)
    

    def not_implemented(self, node):
        raise NotImplementedError(f"No gen for '{node.label}'")


    def gen_Program(self, node):
        self.generate(node.args[1])


    def gen_ProgramDeclaration(self, node: Node):
        # 1) Nome do programa
        self.program_name = node.args[0].args[0]
        program_scope_node = node.args[1]  # <Scope> ou similar

        # 2) Primeiro, pular para main (para não cair nas funções imediatamente)
        self.em.emit("JUMP main")

        # 3) Identificar se existe um nó ManyDeclarations ou não
        # Se existir, será o primeiro filho; senão, o primeiro filho é 
        # diretamente o StatementBlock do main.
        has_decls = False
        if len(program_scope_node.args) >= 1:
            primeiro_filho = program_scope_node.args[0]
            if primeiro_filho.label == "ManyDeclarations":
                has_decls = True

        # 4) Se houver declarações, separar FunctionDeclaration e VarDeclaration
        if has_decls:
            decls = program_scope_node.args[0]  # ponteiro para ManyDeclarations

            # 4.1) Gerar apenas funções antes do main:
            def gerar_funcoes(node):
                if node.label == "FunctionDeclaration":
                    self.generate(node)
                elif node.label == "ManyDeclarations":
                    for child in node.args:
                        gerar_funcoes(child)
                # ignora VarDeclaration aqui

            gerar_funcoes(decls)

        # 5) Agora escrevemos o rótulo de entrada do main e o START
        self.em.emit("main:")
        self.em.emit("START")

        # 6) Se houver declarações, gerar VarDeclaration antes do bloco de statements
        if has_decls:
            def gerar_variaveis_main(node):
                if node.label == "VarDeclaration":
                    self.generate(node)
                elif node.label == "ManyDeclarations":
                    for child in node.args:
                        gerar_variaveis_main(child)
                # ignora FunctionDeclaration aqui

            gerar_variaveis_main(decls)

        # 7) Gerar o StatementBlock do main, que será:
        #    - Se tinha declarações, segundo filho de program_scope_node (args[1])
        #    - Se não tinha declarações, primeiro filho (args[0])
        if has_decls:
            main_block = program_scope_node.args[1]
        else:
            main_block = program_scope_node.args[0]

        # 8) Gerar o conteúdo do bloco principal
        self.generate(main_block)

        # 9) Por fim, emitir STOP
        self.em.emit("STOP")



    def gen_Scope(self, node):
        for stmt in node.args:
            self.generate(stmt)


    def gen_StatementBlock(self, node):
        for stmt in node.args:
            self.generate(stmt)


    def gen_Statement(self, node):
        self.generate(node.args[0])


    def gen_NoTailStatement(self, node):
        self.generate(node.args[0])


    def gen_VarDeclaration(self, node):
        """
        1. Character
        Typically a single octet (one byte). This is an integer type.
        2. Integer
        The most natural size of integer for the machine.
        3. Real
        A single-precision floating point value.
        4. Boolean
        Specifies true or false logical values. This is also an integer type.
        5. Enumerated
        Specifies a user-defined list.
        6. Subrange
        Represents variables, whose values lie within a range.
        7. String
        Stores an array of characters.
        """
        many_param_tuples_node = node.args[0]

        for param_tuple_node in many_param_tuples_node.args:
            many_declared_node = param_tuple_node.args[0]
            return_type_node = param_tuple_node.args[1]
            var_type_node = return_type_node.args[0]

            for declared_node in many_declared_node.args:
                var_name = declared_node.args[0]
                self.em.emit(f"// declaração da variável {var_name}")
                
                if var_type_node.label == 'SimpleType' and var_type_node.args[0].lower() == 'integer':
                    self.em.emit(f"PUSHI 0")
                elif var_type_node.label == 'SimpleType' and var_type_node.args[0].lower() == 'string':
                    self.em.emit('PUSHS ""')
                elif var_type_node.label == 'SimpleType' and var_type_node.args[0].lower() == 'boolean':
                    self.em.emit('PUSHI 0')
                elif var_type_node.label == 'ArrayType':
                    range_node = var_type_node.args[0]
                    self.generate(range_node) # calcula range em runtime
                    self.em.emit("ALLOCN")
                else:
                    raise Exception(f"Variable type '{var_type_node.label}::{var_type_node.args[0]}' not accepted in declaration.")

                self.scope.declare(var_name)
                # # Salva a variável no global_vars dict com o respectivo index
                # self.global_vars[var_name] = self.global_var_counter
                # self.global_var_counter += 1


    def gen_DeclaredName(self, node):
        var_name = node.args[0]
        var_idx = self.scope.lookup(var_name)

        if var_idx is None:
            print(self.scope.scopes)
            raise Exception(f"Variable '{var_name}' not declared.")

        self.em.emit(f"// ler variável {var_name}")
        self.em.emit(f"PUSHL {var_idx}")


    def gen_Assignment(self, node):
        self.generate(node.args[1]) # resolve the right-side expression 
        var_name = node.args[0].args[0] # left-side variable name
        var_idx = self.scope.lookup(var_name)

        if var_idx is not None:
            self.em.emit(f"// assign da var {var_name}")
            self.em.emit(f"STOREL {var_idx}")
        elif var_name in self.declared_funcs:
            return # faça nada
        else:
            print(self.scope.scopes)
            raise Exception(f"Assignment to undeclared variable '{var_name}'")


########################################################################
# 2.1. CONTROL FLOW
########################################################################


    def gen_IfThenElse(self, node):
        condition_node = node.args[0]
        self.generate(condition_node) # resolve condition

        else_label = self.em.new_label()
        endif_label = self.em.new_label()

        self.em.emit(f"JZ {else_label}")

        self.em.emit("// then")
        self.generate(node.args[1])
        self.em.emit(f"JUMP {endif_label}")

        self.em.emit("// else")
        self.em.emit(f"{else_label}:") # else label
        self.generate(node.args[2])

        self.em.emit("// endif")
        self.em.emit(f"{endif_label}:") # code after the if condition


    def gen_IfThen(self, node):
        condition_node = node.args[0]
        self.generate(condition_node) # resolve condition

        # else_label = self.em.new_label()
        endif_label = self.em.new_label()

        self.em.emit("// if")
        self.em.emit(f"JZ {endif_label}")

        self.em.emit("// then")
        self.generate(node.args[1])
        self.em.emit(f"JUMP {endif_label}")

        # self.em.emit("// else")
        # self.em.emit(f"{else_label}:") # else label
        # self.generate(node.args[2])

        self.em.emit("// endif")
        self.em.emit(f"{endif_label}:") # code after the if condition

    
    def gen_For(self, node: Node):
        # condition nodes
        assign_node = node.args[0]
        iterable_var_node = assign_node.args[0]
        iter_limit_node = node.args[2]
        iterable_var_name = iterable_var_node.args[0]
        # body node
        body_node = node.args[3]
        for_loop_type = node.args[1] # downto | to

        for_label = self.em.new_label()
        end_for_label = self.em.new_label()

        # ao inicio, resolve primeiro o assign
        self.em.emit("// for")
        self.generate(assign_node) # resolve left-side

        # cria label
        self.em.emit(f"{for_label}:")

        # verifica condicao do loop
        self.generate(iterable_var_node) # resolve declared name
        self.generate(iter_limit_node) # resolve declared name

        if for_loop_type == 'to': self.em.emit("INFEQ")
        else: self.em.emit("SUPEQ")

        # caso falhe, sai do loop
        self.em.emit(f"JZ {end_for_label}")

        # corpo do loop
        self.generate(body_node)

        # incrementa variável do loop e volta ao inicio
        iterable_var_idx = self.scope.lookup(iterable_var_name)
        # if iterable_var_name not in self.global_vars:
        if iterable_var_idx is None:
            raise Exception(f"Variable '{iterable_var_name}' not declared.")

        self.em.emit("// atualiza variável do foor loop")
        self.em.emit(f"// ler variável {iterable_var_name}")
        self.em.emit(f"PUSHL {iterable_var_idx}")
        self.em.emit("PUSHI 1")

        if for_loop_type == 'to': self.em.emit("ADD")
        else: self.em.emit("SUB")

        self.em.emit(f"STOREL {iterable_var_idx}")

        self.em.emit(f"// voltar ao inicio do loop {for_label}")
        self.em.emit(f"JUMP {for_label}")

        # fim do loop
        self.em.emit(f"// fim do loop {for_label}")
        self.em.emit(f"{end_for_label}:")


    def gen_While(self, node: Node):
        condition_exp_node = node.args[0]
        body_stmt_node = node.args[1]

        while_label = self.em.new_label()
        end_while_label = self.em.new_label()

        self.em.emit("// while loop")
        self.em.emit(f"{while_label}:")

        # 1) resolve condition
        self.em.emit("// condição")
        self.generate(condition_exp_node)
        self.em.emit(f"JZ {end_while_label}")

        # 2) compila o body
        self.generate(body_stmt_node)

        # 3) retorna ao início do loop
        self.em.emit(f"JUMP {while_label}")

        # 4) fim do loop
        self.em.emit(f"// fim do loop {while_label}")
        self.em.emit(f"{end_while_label}:")
    

    def gen_RoutineCall(self, node: Node):
        func_name = node.args[0].args[0]
        func_return = node.args[0].args[1]
        func_params = reversed(node.args[1].args)  # ManyExpressions reversed

        # empilha parâmetros em reversed e verifica se os tipos estão corretos
        for param_idx, param in enumerate(func_params):
            # verifica se o tipo do parâmetro corresponde ao esperado na declaração da função
            if func_name in self.declared_funcs:
                expected_types = self.declared_funcs[func_name]["params"]
                if param_idx < len(expected_types):
                    actual_type = self.infer_type(param)
                    expected_type = expected_types[param_idx]
                    if actual_type != expected_type:
                        raise Exception(f"Parameter {len(list(func_params))-param_idx+1} in call to '{func_name}' expected '{expected_type}', but got '{actual_type}'.")
            self.generate(param)
            # # Verifica se o tipo do parâmetro corresponde ao esperado na declaração da função
            # if func_name in self.declared_funcs:
            #     expected_types = self.declared_funcs[func_name]["params"]
            #     param_index = len(node.args[1].args) - 1 - list(func_params).index(param)
            #     if param_index < len(expected_types):
            #         actual_type = self.infer_type(param)
            #         expected_type = expected_types[param_index]
            #         if actual_type != expected_type:
            #             raise Exception(f"Tipo do parâmetro {param_index+1} na chamada de '{func_name}' esperado '{expected_type}', mas recebeu '{actual_type}'.")
            # self.generate(param)
        if func_return != "Unknown":
            self.em.emit("// empilha slot para retorno")
            self.em.emit("PUSHI 0")

        # call built-in func
        if func_name in self.builtin_funcs:
            return self.builtin_funcs[func_name](node)
        if func_name in self.declared_funcs:
            self.em.emit(f"// chama função {func_name}")
            self.em.emit(f"PUSHA {func_name}")
            self.em.emit("CALL")
        else:
            raise NotImplementedError(f"Function {func_name} not defined")


########################################################################
# 3. DECLARATION RULES
# A declaration is a construct that announces existance of something.
# ex: defining functions/procedures/variables
########################################################################


    def gen_ManyDeclarations(self, node: Node):
        for declaration in node.args:
            self.generate(declaration)
    

    def gen_FunctionDeclaration(self, node: Node):
        # 1) Extrair o nome da função e registrar que ela existe
        func_heading_node = node.args[0]
        func_name = func_heading_node.args[0].args[0]

        # 2) Extrair o tipo de retorno da função
        return_type_node = node.args[1]
        func_return_type = return_type_node.args[0].args[0]

        # 3) extrair tipos dos parâmetros da árvore AST
        param_types: list[str] = []
        routine_params_node = func_heading_node.args[1]
        if len(routine_params_node.args) > 0:
            many_param_tuples = routine_params_node.args[0]
            for param_tuple in many_param_tuples.args:
                return_type = param_tuple.args[1].args[0].args[0]
                for _ in param_tuple.args:
                    param_types.append(return_type)

        # 4) registrar a função com retorno e assinatura
        self.declared_funcs[func_name] = {
            "return_type": func_return_type,
            "params": param_types
        }

        # 2) entrar em escopo local
        self.scope.push()

        # 2) Registrar cada parâmetro como “variável já declarada”
        #    Vamos empurrar esses nomes em self.global_vars.
        #    (Se você quiser tratar parâmetros como variáveis “globais”,
        #     basta adicioná-los aqui. No futuro, depois, você poderia
        #     estender para um dicionário de locais e tratar escopos.)
        routine_params = func_heading_node.args[1]  # nó RoutineParameters
        # Se não houver parâmetros (LPAREN RPAREN), args será vazio ou tamanho 1 sem filhos.
        if len(routine_params.args) > 0:
            many_param_tuples = routine_params.args[0]  # nó ManyParameterTuples
            for param_tuple in many_param_tuples.args:
                # Cada param_tuple é um nó ParameterTuple
                many_declared = param_tuple.args[0]    # nó ManyDeclaredNames
                # Em ManyDeclaredNames, temos uma lista de DeclaredName
                for declared_name_node in many_declared.args:
                    var_name = declared_name_node.args[0]
                    # 2.1) Garantir que não haja colisão
                    if self.scope.lookup(var_name):
                        raise Exception(f"Parâmetro '{var_name}' já declarado em outro lugar.")
                    # 2.2) “Alocar” esse parâmetro em gp[] (mesma lógica de variável)
                    self.em.emit(f"// declaração de parâmetro {var_name} da função {func_name}")
                    self.em.emit("PUSHI 0") # valor inicial
                    self.em.emit(f"STOREG {self.scope.declare(var_name)}")
        
        # 3) Agora podemos emitir o label da função e gerar todo o corpo
        self.em.emit(f"// declaração da função {func_name}")

        self.em.emit(f"{func_name}:")

        # 4) Empilhar parâmetros:
        if len(routine_params.args) > 0:
            self.em.emit(f"// Empilhar parâmetros")
            many_param_tuples = routine_params.args[0]
            for param_tuple in many_param_tuples.args:
                many_declared = param_tuple.args[0]
                # para cada parâmetro
                for param_index, declared_name_node in enumerate(many_declared.args):
                    self.em.emit("PUSHFP")
                    # Para cada parâmetro, empilha o valor correto do frame pointer
                    # O primeiro parâmetro está em FP-2, o segundo em FP-3, etc.
                    # param_index = many_declared.args.index(declared_name_node)
                    self.em.emit(f"LOAD {-2 - param_index}")

        # 4) Gerar o corpo da função (Scope)
        func_scope_node = node.args[2]
        self.generate(func_scope_node)

        # 5) salva no return
        self.em.emit("// salva no return slot")
        self.em.emit("STOREL -1")

        # 6) clean-up
        # para cada parâmetro, faz POP para limpar a stack
        if len(routine_params.args) > 0:
            self.em.emit("// clean-up")
            many_param_tuples = routine_params.args[0]
            for param_tuple in many_param_tuples.args:
                many_declared = param_tuple.args[0]
                for _ in many_declared.args:
                    self.em.emit("POP 1")

        # 5) Epílogo: ao final, se o programador não tiver atribuído
        #    nenhum valor de retorno, talvez você queira emitir erro ou
        #    simplesmente retornar 0 por padrão. Supondo que o retorno
        #    já tenha sido colocado em gp[] pelo STOREL (ou deixou em pilha),
        #    basta chamar RETURN.
        self.em.emit("RETURN")

        # 6) sair do escopo
        self.scope.pop()

        # 6) (Opcional) Se você quiser “remover” do escopo os parâmetros
        #    depois da função, pode dar um pop no dicionário. Exemplo:
        # for param_node em many_param_tuples: del self.global_vars[param_name]
        # Mas cuidado: se houver recursão, talvez queira mantê-los.
        # Nesta versão simples, deixamos como está (parâmetros ficam válidos
        # para qualquer chamada a partir deste ponto).




    def gen_ValueRange(self, node: Node):
        min_node = node.args[0]
        max_node = node.args[1]
        
        self.generate(max_node) # resolve max value
        self.generate(min_node) # resolve min value
        self.em.emit("SUB") # subtrai valores
        # adiciona 1
        self.em.emit("PUSHI 1")
        self.em.emit("ADD")
    

    def gen_ConstantValue(self, node: Node):
        self.generate(node.args[0])


########################################################################
# 4. EXPRESSION RULES
# An expression is a construct that returns a value.
# ex: a * b, function, true AND false, -1, etc
########################################################################


    def gen_Expression(self, node):
        self.generate(node.args[0])


    def gen_MultExpression(self, node: Node):
        left_node = node.args[0]
        right_node = node.args[2]
        mult_operator = node.args[1] # TIMES | INTDIV | REALDIV | MOD

        self.generate(left_node)
        self.generate(right_node)
        self.generate(mult_operator)
    

    def gen_LiteralValue(self, node):
        # LiteralValue : STRINGVALUE
        #      | CHARVALUE
        #      | INTVALUE
        #      | REALVALUE
        #      | TRUE
        #      | FALSE
        literal_type = node.args[0]
        literal_value = node.args[1]

        # FIXME: criar para outros literal values
        self.em.emit(f'// literal value {literal_value}')
        if literal_type == "STRINGVALUE":
            self.em.emit(f'PUSHS "{literal_value}"')
        elif literal_type == 'CHARVALUE':
            # remove as aspas simples
            ch = literal_value.strip("'")
            ascii_code = ord(ch)  # código ASCII
            self.em.emit(f"PUSHI {ascii_code}") # empilha código ASCII
        elif literal_type == "INTVALUE":
            self.em.emit(f'PUSHI {literal_value}')
        elif literal_type == "TRUE":
            self.em.emit(f'PUSHI 1')
        elif literal_type == "FALSE":
            self.em.emit(f'PUSHI 0')
        else:
            raise Exception(f"Literal type '{literal_type}' not supported.")


    def gen_RelOperator(self, node: Node):
        self.generate(node.args[0])

    
    def gen_AndExpression(self, node: Node):
        # 1) Gera código para o operando esquerdo (deixa 0 ou 1 na pilha)
        self.generate(node.args[0])

        # 2) Gera código para o operando direito (deixa 0 ou 1 na pilha)
        self.generate(node.args[1])

        # 3) Emite MUL, que empilha (x * y)
        self.em.emit("MUL")


    def gen_RelExpression(self, node: Node):
        left_node = node.args[0]
        right_node = node.args[2]
        logic_op_node = node.args[1]

        self.generate(left_node) # resolve left-side
        self.generate(right_node) # resolve right-side
        self.generate(logic_op_node)

    
    def gen_AddExpression(self, node: Node):
        left_node = node.args[0]
        right_node = node.args[2]

        self.generate(left_node)
        self.generate(right_node)
        self.em.emit("ADD")

    
    def gen_PrimaryExpression(self, node: Node):
        self.generate(node.args[0])


    def gen_ArrayAccess(self, node: Node):
        declared_node = node.args[0]

        # ajusta para o offset 0-based se for um array access do tipo NÃO string
        if declared_node.args[1].label == 'SimpleType' and declared_node.args[1].args[0] == 'string':
            # empilha string
            # empilha índice
            # CHARAT
            self.em.emit("// string index access")
            self.em.emit("// empilha endereço")
            declared_node = node.args[0]
            self.generate(declared_node)

            self.em.emit("// empilha índice")
            access_index_expr = node.args[1]
            self.generate(access_index_expr)

            self.em.emit("// ajusta para o offset 0-based")
            self.em.emit("PUSHI 1")
            self.em.emit("SUB")

            self.em.emit("CHARAT")
        else:
            self.em.emit("// array access")
            # empilha endereço
            self.em.emit("// empilha endereço")
            self.generate(declared_node)

            # empilha índice
            self.em.emit("// empilha índice")
            access_index_expr = node.args[1]
            self.generate(access_index_expr)

            self.em.emit("// ajusta para o offset 0-based")
            lower_bound_node = declared_node.args[1].args[0].args[0]
            self.generate(lower_bound_node)
            self.em.emit("SUB")

            self.em.emit("LOADN")
        # // leitura no array
        # PUSHG 0 push do endereco
        # PUSHI 1 push do indice
        # LOADN load


    def _gen_write(self, node):
        self.em.emit("// builtin function write")
        for expr in node.args[1].args:
            if expr.args[0].label == 'LiteralValue':
                literal_expr = expr.args[0]

                if literal_expr.args[0] == 'STRINGVALUE':
                    self.em.emit(f"WRITES")
                elif literal_expr.args[0] == 'INTVALUE':
                    self.em.emit(f"WRITEI")
            elif expr.args[0].label == 'DeclaredName':
                declared_type = expr.args[0].args[1]

                if declared_type == 'Integer':
                    self.em.emit(f"WRITEI")

            else:
                raise Exception(f'WRITE - SemanticError: Expected "LiteralValue" or whitespace but {expr.args[0].label} found')


    def _gen_writeln(self, node):
        self.em.emit("// builtin function writeln")
        many_expr = node.args[1]

        for expr in many_expr.args:
            expr_type_node = expr.args[0]

            declared_type_node = expr_type_node.args[1]

            if expr_type_node.label == 'LiteralValue':
                literal_expr = expr.args[0]

                if literal_expr.args[0] == 'STRINGVALUE':
                    self.em.emit(f"WRITES")
                elif literal_expr.args[0] == 'INTVALUE':
                    self.em.emit(f"WRITEI")
                else:
                    raise Exception(f"WRITELN - SemanticError: Literal type '{literal_expr.args[0]}' not supported.")
            elif expr_type_node.label == 'DeclaredName' and declared_type_node.label == 'SimpleType':
                type_label = declared_type_node.args[0]

                if type_label.lower() == 'integer':
                    self.em.emit(f"WRITEI")
                elif type_label.lower() == 'string':
                    self.em.emit(f"WRITES")
                else:
                    raise Exception(f"WRITELN - SemanticError: Declared type '{type_label}' not supported.")
            elif expr_type_node.label == "ArrayAccess":
                array_type = expr_type_node.args[0].args[1].args[0]
                if array_type.lower() == 'integer':
                    self.em.emit(f"WRITEI")
                elif array_type.lower() == 'string':
                    self.em.emit(f"WRITECHR")
                else:
                    raise Exception(f"WRITELN - SemanticError: Array type '{type_label}' not supported.")
            elif expr_type_node.label == "RoutineCall":
                routine_return_type = self.infer_type(expr_type_node)
                if routine_return_type == "Integer":
                    self.em.emit("WRITEI")
                else:
                    raise Exception(f"WRITELN - SemanticError: RoutineCall return type '{routine_return_type}' not supported.")

            else:
                raise Exception(f'WRITELN - SemanticError: Expected ["LiteralValue"|"DeclaredName"|"ArrayAccess"|"RoutineCall"] or whitespace but "{expr_type_node.label}" found')

        self.em.emit("WRITELN")


    def _gen_readln(self, node):
        self.em.emit("// builtin function readln")
        many_expr = node.args[1]

        for expr in many_expr.args:
            expr_type_node = expr.args[0]

            declared_name = expr_type_node.args[0]
            declared_type_node = expr_type_node.args[1]

            if expr_type_node.label == 'DeclaredName' and declared_type_node.label == 'SimpleType':
                type_label = declared_type_node.args[0]

                if type_label.lower() == 'integer':
                    self.em.emit(f"READ")
                    self.em.emit(f"ATOI")

                    var_global_pointer = self.scope.lookup(declared_name)
                    self.em.emit(f"STOREG {var_global_pointer}")
                elif type_label.lower() == 'string':
                    self.em.emit("READ")
                    var_global_pointer = self.scope.lookup(declared_name)
                    self.em.emit(f"STOREG {var_global_pointer}")
                else:
                    raise Exception(f"READLN - SemanticError: Variable type '{declared_type_node.label}::{type_label}' not supported for readln.")
            
            elif expr_type_node.label == 'ArrayAccess':
                array_type = declared_name.args[1].args[1].args[0]
                index_expr_node = expr_type_node.args[1]

                if array_type.lower() != 'integer':
                    raise Exception(f"READLN - SemanticError: Array type '{array_type}' not supported for readln.")

                self.em.emit("// array access")

                self.em.emit("// empilha endereço")
                self.generate(declared_name) # põe endereço na stack

                self.em.emit("// empilha índice")
                self.generate(index_expr_node) # resolve valor do index em runtime

                # ajusta para 0-based
                self.em.emit("// ajusta para o offset 0-based")
                lower_bound_node = declared_name.args[1].args[0].args[0]
                self.generate(lower_bound_node)
                self.em.emit("SUB")

                # lê do input e põe valor na stack
                self.em.emit(f"READ")
                self.em.emit(f"ATOI")

                self.em.emit("STOREN")

            else:
                raise Exception(f'READLN - SemanticError: Expected "DeclaredName" of ["SimpleType"|"ArrayAccess"] but {expr.args[0].label} of {declared_type_node.label} found.')

        self.em.emit("WRITELN")


    def _gen_length(self, node):
        self.em.emit("// builtin function length")
        self.em.emit("STRLEN")


########################################################################
# 4.1. OPERATORS
########################################################################


    def gen_MultOperator(self, node: Node):
        self.generate(node.args[0])


    def gen_STRING(self, node):
        value = node.args[0]
        self.em.emit(f"PUSHS \"{value}\"")


    def gen_NUMBER(self, node):
        value = int(node.args[0])
        self.em.emit(f"PUSHI {value}")


    def gen_TIMES(self, node):
        self.em.emit("MUL")


    def gen_INTDIV(self, node):
        self.em.emit("DIV")


    def gen_MOD(self, node):
        self.em.emit("MOD")
    

    def gen_GT(self, node):
        self.em.emit("SUP")


    def gen_LT(self, node):
        self.em.emit("INF")


    def gen_LTE(self, node):
        self.em.emit("INFEQ")


    def gen_EQ(self, node):
        self.em.emit("EQUAL")


    def infer_type(self, node: Node) -> str:
        label = node.label

        # 1) Literais
        if label == "LiteralValue":
            lit_kind = node.args[0] # ex.: "INTVALUE", "STRINGVALUE", "TRUE", "FALSE"
            if lit_kind == "INTVALUE":
                return "Integer"
            elif lit_kind == "STRINGVALUE":
                return "String"
            elif lit_kind == "TRUE" or lit_kind == "FALSE":
                return "Boolean"
            else:
                raise Exception(f"Literal '{lit_kind}' não suportado em infer_type.")

        # 2) DeclaredName: pode ser variável (local ou global) ou função (uso em expr)
        if label == "DeclaredName":
            name = node.args[0]
            # 2.1) primeiro, verificar se é variável no escopo atual
            idx = self.scope.lookup(name)
            if idx is not None:
                return node.args[1].args[0]
                # # se estiver em 'declared_dict', seu tipo foi registrado no parser ou em VarDeclaration
                # if name in self.declared_dict:
                #     return self.declared_dict[name]
                # else:
                #     # se não houver tipo em declared_dict, assumimos 'Unknown' (não deveria ocorrer)
                #     raise Exception(f"Variável '{name}' declarada mas sem tipo registrado.")
            # 2.2) senão, verificar se é função
            if name in self.declared_funcs:
                return self.declared_funcs[name]["return_type"]
            # 2.3) não foi declarado em nenhuma das duas
            raise Exception(f"Identificador '{name}' não declarado em nenhum escopo.")

        # 3) AddExpression: soma de dois inteiros -> inteiro
        if label == "AddExpression":
            left = node.args[0]
            right = node.args[2]
            t_left = self.infer_type(left)
            t_right = self.infer_type(right)
            if t_left != "Integer" or t_right != "Integer":
                raise Exception(f"Operador '+' exige Integer + Integer, mas recebeu {t_left} + {t_right}.")
            return "Integer"

        # 4) MultExpression: multiplicação, DIV, MOD -> inteiro
        if label == "MultExpression":
            left = node.args[0]
            right = node.args[2]
            # o próprio nó filho <MultOperator> define qual instrução (MUL, DIV, MOD)
            t_left = self.infer_type(left)
            t_right = self.infer_type(right)
            if t_left != "Integer" or t_right != "Integer":
                raise Exception(f"Operador '{node.args[1].args[0]}' exige Integer + Integer, mas recebeu {t_left} e {t_right}.")
            return "Integer"

        # 5) RelExpression: m < n, m > n, m = n etc. -> Boolean
        if label == "RelExpression":
            left = node.args[0]
            op_node = node.args[1]
            right = node.args[2]
            t_left = self.infer_type(left)
            t_right = self.infer_type(right)

            # para comparar strings (EQUAL) ou inteiros
            if op_node.label == "EQ":
                # igualdade genérica: só strings == strings ou inteiros == inteiros
                if t_left == t_right and (t_left in ("Integer", "String")):
                    return "Boolean"
                else:
                    raise Exception(f"Operador '=' exige ambos operandos do mesmo tipo (Integer ou String), mas recebeu {t_left} e {t_right}.")
            else:
                # comparações numéricas: <, >, <=, >=, <>
                if t_left == "Integer" and t_right == "Integer":
                    return "Boolean"
                else:
                    raise Exception(f"Operador relacional '{op_node.args[0]}' exige Integer, mas recebeu {t_left} e {t_right}.")

        # 6) AndExpression: lógica AND -> Boolean
        if label == "AndExpression":
            left = node.args[0]
            right = node.args[1]
            t_left = self.infer_type(left)
            t_right = self.infer_type(right)
            if t_left != "Boolean" or t_right != "Boolean":
                raise Exception(f"Operador 'and' exige Boolean AND Boolean, mas recebeu {t_left} e {t_right}.")
            return "Boolean"

        # 7) Expression ou PrimaryExpression encapsulam um único filho
        if label in ("Expression", "PrimaryExpression"):
            return self.infer_type(node.args[0])

        # 8) RoutineCall: chamar função -> tipo de retorno da função
        if label == "RoutineCall":
            func_node = node.args[0]          # <DeclaredName> com nome da função
            func_name = func_node.args[0]
            if func_name not in self.declared_funcs:
                raise Exception(f"'{func_name}' não é função conhecida.")
            func_info = self.declared_funcs[func_name]
            expected_params = func_info["params"] # ex.: ["Integer", "Integer"]
            actual_args = []
            if len(node.args) > 1:
                for expr_node in node.args[1].args:
                    # cada expr_node é <Expression>; o filho é <LiteralValue> ou <DeclaredName> etc.
                    actual_args.append(self.infer_type(expr_node.args[0]))
            if len(actual_args) != len(expected_params):
                raise Exception(f"Função '{func_name}' esperava {len(expected_params)} parâmetros, recebeu {len(actual_args)}.")
            for exp_t, act_t in zip(expected_params, actual_args):
                if exp_t != act_t:
                    raise Exception(f"Na chamada '{func_name}', parâmetro esperava '{exp_t}', mas recebeu '{act_t}'.")
            return func_info["return_type"]

        # 9) ArrayAccess: arr[i] ou s[i] -> tipo do elemento
        if label == "ArrayAccess":
            declared = node.args[0] # <DeclaredName> com nome do array ou string
            idx_expr = node.args[1]
            t_idx = self.infer_type(idx_expr)
            if t_idx != "Integer":
                raise Exception(f"Índice de acesso deve ser Integer, mas recebeu {t_idx}.")
            arr_name = declared.args[0]
            # verificar se existe variável
            idx = self.scope.lookup(arr_name)
            if idx is not None:
                # tipo vem de declared_dict, que para array seria algo como "Array<Integer>"
                if arr_name not in self.declared_dict:
                    raise Exception(f"'{arr_name}' declarado mas sem tipo registrado.")
                arr_type = self.declared_dict[arr_name]       # ex.: "Array<Integer>" ou "String"
                if arr_type.startswith("Array<"):
                    # extrair tipo de dentro de "Array<...>"
                    elem_type = arr_type[len("Array<") : -1]
                    return elem_type
                elif arr_type == "String":
                    # acesso a caractere de string retorna Integer (código ASCII)
                    return "Integer"
                else:
                    raise Exception(f"'{arr_name}' não é array nem string (é {arr_type}).")
            else:
                raise Exception(f"'{arr_name}' não declarado em nenhum escopo.")

        # 10) outros casos (caso estenda para NotExpression etc.)
        raise Exception(f"infer_type não implementado para nó '{label}'.")