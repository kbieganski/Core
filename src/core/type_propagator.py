from .visitor import *
from .ast import *


class TypePropagator(Visitor):
    @visitor(Assignment)
    def visit(self, node):
        self.iterate(node)
        if not node.lhs.type:
            node.lhs.target.type = Reference(node.rhs.type.target)
            node.lhs.type = Reference(node.rhs.type.target)
        assert node.lhs.type.target == node.rhs.type.target
        node.type = node.lhs.type

    @visitor(BinaryOp)
    def visit(self, node):
        self.iterate(node)
        assert node.left.type.target and node.left.type.target == node.right.type.target
        node.type = node.left.type


def propagate_types(root):
    TypePropagator().visit(root)
