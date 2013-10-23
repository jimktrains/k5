import pprint
from pyparsing import *
import sys

print("So, this doesn't work and references and older version of the lang")
exit()
 
ParserElement.setDefaultWhitespaceChars(' \t')

AS = CaselessKeyword("AS")
WITH = CaselessKeyword("WITH")
FOLD = CaselessKeyword("FOLD")
MAP = CaselessKeyword("MAP")
REDUCE = CaselessKeyword("REDUCE")
L = CaselessKeyword("L")
INTEGER = CaselessKeyword("INTEGER")
PRINT = CaselessKeyword("PRINT")
IF = CaselessKeyword("IF")
ELSE = CaselessKeyword("ELSE")
TRUE = CaselessKeyword("TRUE")
FALSE = CaselessKeyword("FALSE")
BOOLEAN = CaselessKeyword("BOOLEAN")
ATTRIBUTES = CaselessKeyword("ATTRIBUTES")
DIM = CaselessKeyword("DIM")
NONE = CaselessKeyword("NONE")
STRING = CaselessKeyword("STRING")
CLASS = CaselessKeyword("CLASS")
METHODS = CaselessKeyword("METHODS")

keyword = MatchFirst( 
[
    ATTRIBUTES,
    DIM,
    AS,
    WITH,
    FOLD,
    MAP,
    REDUCE,
    L,
    INTEGER,
    PRINT,
    IF,
    ELSE,
    TRUE,
    FALSE,
    BOOLEAN,
    NONE,
    STRING,
    METHODS
]
) 
key_types = MatchFirst( 
[
    INTEGER,
    BOOLEAN,
    NONE,
    STRING 
]
) 
COLON = Suppress(Literal(':'))
item = Forward()
number = Word(nums)
bools = TRUE | FALSE
ident = ~keyword + Word(alphas, alphanums+'_')
operand = number | ident | bools
arexpr = operatorPrecedence(operand, [
    ('-', 1, opAssoc.RIGHT),
    (oneOf('* /'), 2, opAssoc.LEFT),
    (oneOf('+ -'), 2, opAssoc.LEFT),
])

comparisonExpr = operatorPrecedence(operand, [
    (oneOf("< > == <= >= !="), 2, opAssoc.LEFT),
])
booleanExpr = operatorPrecedence(comparisonExpr, [
    ('~', 1, opAssoc.RIGHT),
    (oneOf('& | ^'), 2, opAssoc.LEFT),
])


indentStack = [1]

var_dec = DIM + Group(ident + Suppress(AS) + (ident|key_types))
func_dec = DIM + Group(ident + Suppress(AS) + (ident|key_types))

ATTRIBUTES_BLOCK = ATTRIBUTES + COLON  + indentedBlock(var_dec, indentStack)
METHOD_BLOCK = METHODS + COLON + indentedBlock(func_dec, indentedBlock)
item << OneOrMore( (CLASS + ident + COLON)  +
                   indentedBlock(ATTRIBUTES_BLOCK, indentStack) +
                   indentedBlock(METHOD_BLOCK, indentStack)
)
 
parser = OneOrMore(indentedBlock(item, indentStack, False)) + StringEnd()
 
data = '''
Class test:
    ATTRIBUTES:
        Dim x as Integer
        DIM Y as STRING
    Methods:
        Dim x as Integer
        DIM Y as STRING
'''
print(data)
a = parser.parseString(data)


pprint.pprint( a.asList() )
