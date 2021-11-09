from .visitor import *
from .ast import *

class GlobalGatherer(Visitor):
    def __init__(self):
        self.scope = {}

    @visitor(Function)
    def visit(self, node):
        self.scope[node.name] = node


class IdResolver(Visitor):
    def __init__(self):
        self.scope_stack = []

    def push_scope(self, scope = {}):
        self.scope_stack.append(scope)

    def pop_scope(self):
        self.scope_stack.pop()

    def resolve(self, name):
        for i in range(1, len(self.scope_stack)+1):
            try:
                return self.scope_stack[-i][name]
            except KeyError: pass

    @visitor(Call)
    def visit(self, node):
        print("asdfsdfsdf")
        node.function = self.resolve(node.fn_name)
        print('====>', node.function)

    @visitor(Module)
    def visit(self, node):
        gather_visitor = GlobalGatherer()
        gather_visitor.visit(node)
        self.push_scope(gather_visitor.scope)
        print(gather_visitor.scope)
        for func in node:
            self.visit(func)


