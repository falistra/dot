import ply.yacc as yacc
import ply.lex as lex

import bn_om as bn # semantic i.e object model

tokens = [ # any input get split into tokens
    'ARROW','EQUALS','SEMICOL',
    'LS_PAREN','RS_PAREN','COMMA',
    'NAME',
    'PROBABILITY_VALUE1', 'PROBABILITY_VALUE2'
]

# Tokens
# convention of ply: you need to use the notation t_[token name] = value.
# every token needs to be recognised through regular expression. r'\+' means take + literally.
t_ARROW = r'\-\>'
t_EQUALS = r'\='
t_SEMICOL = r'\;'
t_LS_PAREN = r'\['
t_RS_PAREN = r'\]'
t_COMMA = r'\,'


# for more complex lexical recognition, you make a function
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_PROBABILITY_VALUE1(t):
    r'((0?)\.(\d+))' # I can write .5 for 0.5
    t.value = float(t.value)
    return t

def t_PROBABILITY_VALUE2(t):
    r'0|1'
    t.value = float(t.value)
    return t

t_ignore = u" \t\n" # ignore whitespaces, newlines, tabs.

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def p_dag1(p):
    """ DAG : element"""
    p[0] = bn.BayesianNet() + p[1]

def p_dag2(p):
    """ DAG : element DAG"""
    p[0] = p[2] + p[1]

def p_element1(p):
    """ element : NAME LS_PAREN NAME EQUALS pvalue RS_PAREN"""
    p[0] = bn.InitialNode(p[1])

def p_element2(p):
    """ element : name_list ARROW NAME LS_PAREN tensor RS_PAREN"""
    p[0] = bn.Edge(p[1],bn.Node(p[3]),p[5])

def p_name_list1(p):
    """ name_list : NAME """
    p[0] = [bn.Node(p[1])]

def p_name_list2(p):
    """ name_list : NAME COMMA name_list"""
    p[0] = [bn.Node(p[1])] + p[3]

def p_tensor1(p):
    """ tensor : p_assign"""
    p[0] = {p[1][0] : p[1][1]}

def p_tensor2(p):
    """ tensor : p_assign SEMICOL tensor"""
    p[3].update({p[1][0] : p[1][1]})
    p[0] = p[3]

def p_assign(p):
    """ p_assign : values_list EQUALS pvalue """
    p[0] = (p[1],p[3])

def p_values_list1(p):
    """ values_list : NAME """
    p[0] = bn.valuesList() + p[1]

def p_values_list2(p):
    """ values_list : NAME COMMA values_list"""
    p[0] = p[3] + p[1]

def p_pvalue(p):
    """ pvalue : PROBABILITY_VALUE1
        | PROBABILITY_VALUE2
        """
    p[0] = p[1]

def p_error(p):
    if p:
      print("Syntax error at '%s'" % p.value)
    else:
      print("Syntax error at EOF")

def parse(code):
    lexer = lex.lex()
    parser = yacc.yacc(start="DAG")
    lexer.input(code) # let code be the input of the lexer
    return parser.parse(lexer=lexer)
