from .visitor import *
from .ast import *


class PrimitiveTyper(Visitor):
    def __init__(self):
        self.int8 = Type("int8")
        self.int32 = Type("int32")
        self.func = Type("fn()")
        self.builtin = [self.int8, self.int32, self.func]

    @visitor(Number)
    def visit(self, node):
        node.type = Reference(self.int32)

    @visitor(Function)
    def visit(self, node):
        node.type = Reference(self.func)
        self.iterate(node)

    @visitor(Module)
    def visit(self, node):
        for child in node:
            if isinstance(child, Scope):
                for type in self.builtin:
                    child.register(type.name, type)
                    node.add_child(type)
                node.add_child(child.unlink())
                break
        self.iterate(node)


def primitive_type(root):
    PrimitiveTyper().visit(root)
