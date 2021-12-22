from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('PRINT', r'print')
        self.lexer.add('LET', r'let')
        self.lexer.add('IF', r'if')
        self.lexer.add('FN', r'fn')
        self.lexer.add('ID', r'[A-Za-z][A-Za-z0-9]*')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('OPEN_BRACE', r'\{')
        self.lexer.add('CLOSE_BRACE', r'\}')
        self.lexer.add('SEMICOLON', r'\;')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'\/')
        self.lexer.add('MOD', r'\%')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('EQ', r'==')
        self.lexer.add('NEQ', r'!=')
        self.lexer.add('GEQ', r'>=')
        self.lexer.add('LEQ', r'<=')
        self.lexer.add('ASSIGN', r'\=')
        self.lexer.add('GT', r'>')
        self.lexer.add('LT', r'<')
        # Ignore spaces
        self.lexer.ignore('\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
