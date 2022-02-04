from .visitor import *
from .ast import *

class Scoper(Visitor):
    def __init__(self):
        self.scope = None

    @visitor(VarDecl)
    def visit(self, node):
        scope = Scope([Assignment(Reference(node.name), node.expression)])
        scope.add_children(*node._parent[node.selfref+1:])
        variable = Variable(node.name)
        scope.register(node.name, variable)
        node.replace(variable, scope)
        self.visit(scope) # TODO: do this automatically

    @visitor(Function)
    def visit(self, node):
        self.scope.register(node.name, node)
        scope = Scope(node.block)
        node.block = scope
        for param in node.parameters:
            scope.register(param.name, param)
        self.iterate(node)

    @visitor(Scope)
    def visit(self, node):
        node.parent_scope = self.scope
        self.scope = node
        self.iterate(node)
        self.scope = node.parent_scope

    @visitor(Module)
    def visit(self, node):
        scope = Scope(node)
        node.add_child(scope)
        self.iterate(node)


def scope(root):
    Scoper().visit(root)
