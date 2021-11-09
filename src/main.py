from core import Lexer, Parser, CodeGen, IdResolver
import sys

fname = sys.argv[1]
with open(fname) as f:
    text_input = f.read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

codegen = CodeGen()
id_resolver = IdResolver()

pg = Parser()
pg.parse()
parser = pg.get_parser()
module = parser.parse(tokens)
id_resolver.visit(module)
codegen.visit(module)

codegen.compile_ir()
codegen.save_ir("out.ll")
