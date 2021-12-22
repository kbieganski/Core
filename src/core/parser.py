from rply import ParserGenerator
from .ast import *


class Parser():
    def __init__(self):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUMBER', 'ID', 'FN', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'OPEN_BRACE', 'CLOSE_BRACE',
             'SEMICOLON', 'SUM', 'SUB', 'MUL', 'DIV', 'MOD', 'EQ', 'NEQ', 'GT', 'LT', 'GEQ', 'LEQ',
             'ASSIGN', 'IF', 'LET']
        )

    def parse(self):
        @self.pg.production('program : ')
        def empty_program(p):
            return Module()

        @self.pg.production('program : program function')
        def program(p):
            p[0].append(p[1])
            return p[0]

        @self.pg.production('function : FN ID OPEN_PAREN CLOSE_PAREN block')
        def function(p):
            return Function(p[1].getstr(), p[4])

        @self.pg.production('expression : ID OPEN_PAREN CLOSE_PAREN')
        def function_call(p):
            return Call(p[0].getstr())

        @self.pg.production('print : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print(p):
            return Print(p[2])

        @self.pg.production('block : OPEN_BRACE statements CLOSE_BRACE')
        def block(p):
            return Block(p[1])

        @self.pg.production('if_block : IF expression block')
        def if_block(p):
            return If(p[1], p[2])

        @self.pg.production('statement : print SEMICOLON | expression SEMICOLON | if_block')
        def statement(p):
            return p[0]

        @self.pg.production('statement : LET ID ASSIGN expression')
        def var_declaration(p):
            return VarDecl(p[2], p[4])

        @self.pg.production('statements : ')
        def empty_statements(p):
            return []

        @self.pg.production('statements : statements statement')
        def statements(p):
            p[0].append(p[1])
            return p[0]

        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        @self.pg.production('expression : expression MOD expression')
        @self.pg.production('expression : expression EQ expression')
        @self.pg.production('expression : expression NEQ expression')
        @self.pg.production('expression : expression GT expression')
        @self.pg.production('expression : expression LT expression')
        @self.pg.production('expression : expression GEQ expression')
        @self.pg.production('expression : expression LEQ expression')
        def expression(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'SUM':
                return Sum(left, right)
            elif operator.gettokentype() == 'SUB':
                return Sub(left, right)
            elif operator.gettokentype() == 'MUL':
                return Mul(left, right)
            elif operator.gettokentype() == 'DIV':
                return Div(left, right)
            elif operator.gettokentype() == 'MOD':
                return Mod(left, right)
            elif operator.gettokentype() == 'EQ':
                return Eq(left, right)
            elif operator.gettokentype() == 'NEQ':
                return Neq(left, right)
            elif operator.gettokentype() == 'GT':
                return Gt(left, right)
            elif operator.gettokentype() == 'LT':
                return Lt(left, right)
            elif operator.gettokentype() == 'GEQ':
                return Geq(left, right)
            elif operator.gettokentype() == 'LEQ':
                return Leq(left, right)

        @self.pg.production('expression : NUMBER')
        def number(p):
            return Number(p[0].value)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
