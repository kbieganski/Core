from core import *
import sys

fname = sys.argv[1]
with open(fname) as f:
    text_input = f.read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)


pg = Parser()
pg.parse()
parser = pg.get_parser()
module = parser.parse(tokens)
scope(module)
primitive_type(module)
print_tree(module)
resolve(module)
cast(module)
propagate_types(module)
resolve(module)
print_tree(module)
ir = codegen(module)
with open("out.ll", 'w') as output_file:
    output_file.write(str(ir))
