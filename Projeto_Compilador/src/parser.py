from tree import Node
from ply import yacc
from lexer import tokens, lexer

rootNode = None

########################################################################
# DECLARED VALUES
# Dict to store declared identifiers and their types (variables, functions, procedures, etc.)
# It is essential for semantic analysis, type checking, and for detecting redeclarations or undeclared usage.
########################################################################
declared_dict = {}

########################################################################
# 1. PROGRAM RULES
########################################################################

def p_Program(p): # start here
    """
    Program : PROGRAM ProgramDeclaration 
    """
    global rootNode
    rootNode = Node("Program", p[1], p[2])
    p[0] = rootNode

########################################################################
# 2. STATEMENT RULES
# A statement is a construct that executes an action.
# ex: assign, if-else, loops, procedure
# unlike C, statements are SEPARATED by semicolon
########################################################################

def p_Scope(p):
    """
    Scope : ManyDeclarations StatementBlock
          | StatementBlock
    """
    if len(p)==2 : p[0] = Node("Scope", p[1])
    else:          p[0] = Node("Scope", p[1], p[2])

def p_TerminalSemicolons(p):
    """
    TerminalSemicolons : 
                       | SEMICOLON TerminalSemicolons
    """

def p_StatementBlock(p):
    """
    StatementBlock : BEGIN END
                   | BEGIN ManyStatements TerminalSemicolons END
    """
    if len(p) == 3:
        p[0] = Node("StatementBlock")
    else:
        p[0] = Node("StatementBlock", *p[2].args)

def p_ManyStatements(p):
    """
    ManyStatements : Statement
                   | ManyStatements SEMICOLON Statement
    """
    if len(p) == 2:
        p[0] = Node('ManyStatements', p[1])
    else:
        p[1].add_child(p[3])
        p[0] = p[1]

def p_Statement(p):
    """
    Statement : NoTailStatement
              | IfThen
              | IfThenElse
              | While
              | For
    """
    p[0] = Node("Statement", p[1])

# "closed" statement: all ifs within are ELSE'd
# to avoid ELSE ambiguity, THEN substatements must be closed
def p_ClosedStatement(p):
    """
    ClosedStatement : NoTailStatement
                    | ClosedIfThenElse
                    | ClosedWhile
                    | ClosedFor
    """
    p[0] = p[1]

# "tail" statement: can omit begin-end in single substatement situations
# loops/ifs are tail statements. this induces scope ambiguity
# these kinds of statements below never cause that issue
def p_NoTailStatement(p):
    """
    NoTailStatement : StatementBlock
                    | Assignment
                    | RoutineCall
    """
    p[0] = Node("NoTailStatement", p[1])

def p_Assignment(p):
    """
    Assignment : DeclaredName ASSIGN Expression
    """
    p[0] = Node("Assignment", p[1], p[3])

########################################################################
# 2.1. CONTROL FLOW
########################################################################

def p_IfThen(p):
    """
    IfThen : IF Expression THEN Statement
    """
    p[0] = Node("IfThen", p[2], p[4])
 
def p_IfThenElse(p):
    """
    IfThenElse : IF Expression THEN ClosedStatement ELSE Statement 
    """
    p[0] = Node("IfThenElse", p[2], p[4], p[6])
 
def p_ClosedIfThenElse(p):
    """
    ClosedIfThenElse : IF Expression THEN ClosedStatement ELSE ClosedStatement
    """
    p[0] = Node("IfThenElse", p[2], p[4], p[6])

def p_While(p):
    """
    While : WHILE Expression DO Statement 
    """
    p[0] = Node("While", p[2], p[4])

def p_ClosedWhile(p):
    """
    ClosedWhile : WHILE Expression DO ClosedStatement 
    """
    p[0] = Node("ClosedWhile", p[1],p[2],p[3],p[4])

def p_For(p):
    """
    For : FOR Assignment TO Expression DO Statement
        | FOR Assignment DOWNTO Expression DO Statement 
    """
    p[0] = Node("For", p[2], p[3], p[4], p[6])

def p_ClosedFor(p):
    """
    ClosedFor : FOR Assignment TO Expression DO ClosedStatement
              | FOR Assignment DOWNTO Expression DO ClosedStatement
    """
    p[0] = Node("ClosedFor", p[2], p[3], p[4])

########################################################################
# 3. DECLARATION RULES
# A declaration is a construct that announces existance of something.
# ex: defining functions/procedures/variables
########################################################################

def p_ManyDeclarations(p):
    """
    ManyDeclarations : Declaration
                     | ManyDeclarations Declaration
    """
    #if len(p) == 2: p[0] = p[1]
    #else:
    #    p[1].add_child(p[2])
    #    p[0] = p[1]
    if len(p) == 2: p[0] = Node("ManyDeclarations", p[1])
    else:           p[0] = Node("ManyDeclarations", p[1], p[2])

def p_Declaration(p):
    """
    Declaration : VAR VarDeclaration
                | PROCEDURE ProcedureDeclaration
                | FUNCTION FunctionDeclaration
    """
    p[0] = p[2]

def p_VarDeclaration(p):
    """
    VarDeclaration : ManyParameterTuples SEMICOLON
    """
    p[0] = Node("VarDeclaration", p[1])
    
def p_ProcedureDeclaration(p):
    """
    ProcedureDeclaration : RoutineHeading SEMICOLON Scope SEMICOLON
    """
    p[0] = Node("ProcedureDeclaration", p[1], p[2], p[3], p[4])

def p_FunctionDeclaration(p):
    """
    FunctionDeclaration : RoutineHeading ReturnType SEMICOLON Scope SEMICOLON
    """
    # salvar a declaração da função no dicionário declared_dict
    func_name = p[1].args[0].args[0]
    return_type = p[2]

    declared_dict[func_name] = return_type

    p[0] = Node("FunctionDeclaration", p[1], p[2], p[4])

def p_ProgramDeclaration(p): # start here
    """
    ProgramDeclaration : DeclaredName SEMICOLON Scope DOT 
    """
    p[0] = Node("ProgramDeclaration", p[1], p[3])

def p_RoutineHeading(p):
    """
    RoutineHeading : DeclaredName RoutineParameters
    """
    p[0] = Node("RoutineHeading", p[1], p[2])
    
def p_RoutineParameters(p):
    """
    RoutineParameters :
                      | LPAREN RPAREN
                      | LPAREN ManyParameterTuples RPAREN
    """
    if len(p) == 1:   p[0] = Node("RoutineParameters")
    elif len(p) == 3: p[0] = Node("RoutineParameters")
    else:             p[0] = Node("RoutineParameters", p[2])

def p_ManyParameterTuples(p):
    """
    ManyParameterTuples : ParameterTuple 
                        | ManyParameterTuples SEMICOLON ParameterTuple
    """
    if len(p) == 2: p[0] = Node("ManyParameterTuples", p[1])
    else:
        p[1].add_child(p[3])
        p[0] = p[1]

def p_ParameterTuple(p):
    """
    ParameterTuple : ManyDeclaredNames ReturnType
    """
    # salvar a declaração das variáveis no dicionário declared_dict
    declarations = p[1]
    return_type = p[2].args[0]

    for declaration in declarations.args:
        declaration_name = declaration.args[0]
        declared_dict[declaration_name] = return_type

    p[0] = Node("ParameterTuple", p[1], p[2])

def p_ManyDeclaredNames(p):
    """
    ManyDeclaredNames : DeclaredName
                      | ManyDeclaredNames COMMA DeclaredName 
    """
    if len(p) == 2:
        p[0] = Node('ManyDeclaredNames', p[1])
    else:
        p[1].add_child(p[3])
        p[0] = p[1]

def p_ReturnType(p):
    """
    ReturnType : COLON Type
    """
    p[0] = Node("ReturnType", p[2])    

def p_Type(p):
    """
    Type : SimpleType
         | ArrayType
    """
    p[0] = p[1]

def p_SimpleType(p):
    """
    SimpleType : TYPESTRING
               | TYPEINT
               | TYPEREAL
               | TYPECHAR
               | TYPEBOOL
    """
    p[0] = Node("SimpleType", p[1])    

# in a more thorough implementation:
# - Type instead of SimpleType (enumerable custom datatypes are allowed)
# - ManyRanges instead of Range (for 2D+ arrays)
def p_ArrayType(p):
    """
    ArrayType : ARRAY LSPAREN ValueRange RSPAREN OF SimpleType
    """
    p[0] = Node("ArrayType", p[3], p[6])

def p_ValueRange(p):
    """
    ValueRange : ConstantValue DOTDOT ConstantValue
    """
    p[0] = Node("ValueRange", p[1], p[3])

def p_ConstantValue(p):
    """
    ConstantValue : LiteralValue
                  | DeclaredName
    """
    p[0] = Node("ConstantValue", p[1])    

########################################################################
# 4. EXPRESSION RULES
# An expression is a construct that returns a value.
# ex: a * b, function, true AND false, -1, etc
########################################################################

def p_ManyExpressions(p):
    """
    ManyExpressions : Expression
                    | ManyExpressions COMMA Expression
    """
    if len(p)==2 : p[0] = Node("ManyExpressions", p[1])
    else:
        p[1].add_child(p[3])
        p[0] = p[1]

def p_Expression(p):
    """
    Expression : OrExpression
    """
    p[0] = Node("Expression", p[1])

def p_OrExpression(p):
    """
    OrExpression : AndExpression
                 | OrExpression OR AndExpression 
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("OrExpression", p[1], p[3])

def p_AndExpression(p):
    """
    AndExpression : RelExpression
                  | AndExpression AND RelExpression 
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("AndExpression", p[1], p[3])

def p_RelExpression(p):
    """
    RelExpression : AddExpression
                  | RelExpression RelOperator AddExpression 
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("RelExpression", p[1], p[2], p[3])

def p_AddExpression(p):
    """
    AddExpression : MultExpression
                  | AddExpression AddOperator MultExpression 
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("AddExpression", p[1], p[2], p[3])

def p_MultExpression(p):
    """
    MultExpression : UnaryExpression
                   | MultExpression MultOperator UnaryExpression 
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("MultExpression", p[1], p[2], p[3])

def p_UnaryExpression(p):
    """
    UnaryExpression : UnaryOperator UnaryExpression
                    | PrimaryExpression
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("UnaryExpression", p[1], p[2])

def p_PrimaryExpression(p):
    """
    PrimaryExpression : LiteralValue
                      | LPAREN Expression RPAREN
                      | RoutineCall
                      | ArrayAccess
                      | DeclaredName
    """
    if len(p)==2: p[0] = p[1]
    else:         p[0] = Node("PrimaryExpression", p[2])

def p_LiteralValue(p):
    """
    LiteralValue : STRINGVALUE
                 | CHARVALUE
                 | INTVALUE
                 | REALVALUE
                 | TRUE
                 | FALSE  
    """
    p[0] = Node("LiteralValue", p.slice[1].type, p[1])

def p_ArrayAccess(p):
    """
    ArrayAccess : DeclaredName LSPAREN RSPAREN
                | DeclaredName LSPAREN Expression RSPAREN
    """
    if len(p)==4 : p[0] = Node("ArrayAccess", p[1])
    else:          p[0] = Node("ArrayAccess", p[1], p[3])

def p_DeclaredName(p):
    """
    DeclaredName : IDENTIFIER
    """
    declared_type = "Unknown"
    if p[1] in declared_dict:
        declared_type = declared_dict[p[1]]

    p[0] = Node("DeclaredName", p[1], declared_type)

########################################################################
# 4.1. OPERATORS
########################################################################

def p_RelOperator(p):
    """
    RelOperator : EQ
                | NEQ
                | LT
                | GT
                | LTE
                | GTE
    """
    operator_node = Node(p.slice[1].type)
    p[0] = Node("RelOperator", operator_node)

def p_AddOperator(p):
    """
    AddOperator : PLUS
                | MINUS
    """
    p[0] = Node("AddOperator", p[1])

def p_MultOperator(p):
    """
    MultOperator : TIMES
                 | INTDIV
                 | REALDIV
                 | MOD
    """
    operator_node = Node(p.slice[1].type)
    p[0] = Node("MultOperator", operator_node)

def p_UnaryOperator(p):
    """
    UnaryOperator : PLUS
                  | MINUS
                  | NOT
    """
    p[0] = Node("UnaryOperator", p[1])

def p_RoutineCall(p):
    """
    RoutineCall : DeclaredName LPAREN RPAREN
                | DeclaredName LPAREN ManyExpressions RPAREN
    """
    if len(p)==4 : p[0] = Node("RoutineCall", p[1])
    else:          p[0] = Node("RoutineCall", p[1], p[3])









def p_error(p):
    global rootNode
    if p:
        ###########################################################
        # Get expected tokens from the current parser state
        state = parser.state
        expected_tokens = []
        for tok_type in parser.action[state].keys():
            if tok_type not in ('error', '$end'):
                expected_tokens.append(tok_type)
        
        # Remove duplicates and sort for readability
        expected_unique = sorted(list(set(expected_tokens)))
        expected_str = ", ".join(expected_unique)
        ############################################################
        
        # Get the line where the error occurred
        lines = filecontent.split('\n')
        error_line = lines[p.lineno - 1]
        
        # Calculate the position of the error in the line
        if p.lineno > 1:
            # Sum the lengths of previous lines plus newline characters
            pos_in_line = p.lexpos - sum(len(lines[i]) + 1 for i in range(p.lineno - 1))
        else:
            pos_in_line = p.lexpos
        
        # Create the caret line
        caret_line = ' ' * pos_in_line + '^'
        
        print(f"\n[Ln {p.lineno}] Syntax error: Unexpected '{p.value}' (type {p.type}). Expected: {expected_str}")
        print(f"    {error_line}")
        print(f"    {caret_line}")


        # Existing code for partial syntax tree
        if rootNode is not None:
            print("Partial syntax tree up to the error:")
            print(rootNode)
        else:
            if hasattr(parser, 'symstack'):
                partial_nodes = [sym for sym in parser.symstack if isinstance(sym, Node)]
                if partial_nodes:
                    print("Partial syntax tree up to the error:")
                    print(partial_nodes[-1])
                else:
                    print("No partial tree available (parsing didn't start)")
            else:
                print("Parser stack not available")
        exit(1)
    else:
        print("Syntax error: Unexpected end of input.")
        exit(1)

parser = yacc.yacc(debug=True, write_tables=0)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Argumentos insuficientes")
        exit(1)
        
    filecontent = ""

    with open(sys.argv[1], encoding='utf-8') as input_file:
        filecontent = input_file.read()
        result = parser.parse(filecontent)
        print(" _")
        print(rootNode)