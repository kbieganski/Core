from .visitor import *
from .ast import *

class Printer(Visitor):
    def __init__(self):
        self.indent = ''
        self.indent_step = '    '

    @visitor(Node)
    def visit(self, node):
        repr = self.indent + type(node).__name__
        if hasattr(node, 'name'):
            repr += " '" + node.name + "'"
        if hasattr(node, 'value'):
            repr += " '" + str(node.value) + "'"
        if hasattr(node, 'type'):
            if not (isinstance(node, Reference) and isinstance(node.target, Type)):
                repr += " [" + (str(node.type.name) if node.type else '?') + "]"
        print(repr)
        self.indent += self.indent_step
        self.iterate(node)
        self.indent = self.indent[:-len(self.indent_step)]


def print_tree(root):
    Printer().visit(root)
