from rply import ParserGenerator
from .ast import *


class Parser():
    def __init__(self):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUMBER', 'ID', 'FN', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'OPEN_BRACE', 'CLOSE_BRACE',
             'SEMICOLON', 'COMMA', 'SUM', 'SUB', 'MUL', 'DIV', 'MOD', 'EQ', 'NEQ', 'GT', 'LT', 'GEQ', 'LEQ',
             'ASSIGN', 'IF', 'LET'],
            precedence=[
                    ('left', ['SUM', 'SUB']),
                    ('left', ['MUL', 'DIV', 'MOD']),
                    ('left', ['EQ', 'NEQ', 'GT', 'LT', 'GEQ', 'LEQ']),
                ]
        )

    def parse(self):
        @self.pg.production('program : ')
        def empty_program(p):
            return Module()

        @self.pg.production('program : program function')
        def program(p):
            p[0].add_child(p[1])
            return p[0]

        @self.pg.production('function : ID OPEN_PAREN CLOSE_PAREN block')
        def function(p):
            return Function(p[0].getstr(), p[3])

        @self.pg.production('function : ID OPEN_PAREN parameters CLOSE_PAREN block')
        def function(p):
            #return Function(p[1].getstr(), p[5], ParameterList(p[3]))
            return Function(p[0].getstr(), p[4], p[2])

        @self.pg.production('expression : simple_expression OPEN_PAREN CLOSE_PAREN')
        def function_call(p):
            return Call(p[0])

        @self.pg.production('expression : simple_expression OPEN_PAREN expressions CLOSE_PAREN')
        def function_call(p):
            return Call(p[0], ArgumentList(p[2]))

        @self.pg.production('print : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(p):
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

        @self.pg.production('statement : LET ID ASSIGN expression SEMICOLON')
        def var_declaration(p):
            return VarDecl(p[1].getstr(), p[3])

        @self.pg.production('statements : ')
        def empty_statements(p):
            return []

        @self.pg.production('statements : statements statement')
        def statements(p):
            p[0].append(p[1])
            return p[0]

        @self.pg.production('expressions : expression')
        def expressions_single(p):
            return [p[0]]

        @self.pg.production('expressions : expressions COMMA expression')
        def expressions(p):
            p[0].append(p[2])
            return p[0]

        @self.pg.production('parameters : ID ID')
        def parameters_single(p):
            typeref = Reference(p[1].getstr())
            param = Variable(p[0].getstr(), typeref)
            return VariableList([param])

        @self.pg.production('parameters : parameters COMMA ID ID')
        def parameters(p):
            typeref = Reference(p[3].getstr())
            param = Variable(p[2].getstr(), typeref)
            p[0].add_child(param)
            return p[0]

        @self.pg.production('expression : simple_expression')
        def paren_expr(p):
            return p[0]

        @self.pg.production('simple_expression : OPEN_PAREN expression CLOSE_PAREN')
        def paren_expr(p):
            return p[1]

        @self.pg.production('simple_expression : ID')
        def reference(p):
            return Reference(p[0].getstr())

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

        @self.pg.production('simple_expression : NUMBER')
        def number(p):
            return Number(p[0].value)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
