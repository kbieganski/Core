from .visitor import *
from .ast import *


class Caster(Visitor):
    @visitor(Call)
    def visit(self, node):
        self.iterate(node)
        if isinstance(node.function.target, Type):
            node.replace(Cast(node.function, *node.arguments))


def cast(root):
    Caster().visit(root)
