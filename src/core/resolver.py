from .visitor import *
from .ast import *


class Resolver(Visitor):
    def __init__(self):
        self.scope = None

    @visitor(Reference)
    def visit(self, node):
        node.target = self.scope.resolve(node.name)
        if not isinstance(node.target, Type) and node.target.type:
            node.type = Reference(node.target.type.target)

    @visitor(Scope)
    def visit(self, node):
        self.scope = node
        self.iterate(node)
        self.scope = node.parent_scope


def resolve(root):
    Resolver().visit(root)
