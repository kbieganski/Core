
class Node:
    def __init__(self):
        self._parent = None
        self.selfref = None
        self._children = {}

    def add_child(self, name, node):
        self._children[name] = None
        self[name] = node

    def delete(self):
        self.replace(None)

    def replace(self, new):
        if self._parent:
            self._parent[self.selfref] = new

    def unlink(self):
        self.replace(None)

    def next(self):
        if self._parent:
            try:
                return self._parent[self.selfref + 1]
            except TypeError:
                pass

    def __setitem__(self, name, child):
        del self[name]
        if child:
            self._children[name] = child
            child._parent = self
            child.selfref = name
            super().__setattr__(name, child)

    def __getitem__(self, name):
        return self._children[name]

    def __delitem__(self, name):
        old = self._children[name]
        if old:
            old._parent = None
            old.selfref = None
        super().__setattr__(name, None)

    def __iter__(self):
        for child in self._children.values():
            if child: yield child

    def __setattr__(self, name, child):
        if hasattr(self, '_children') and name in self._children:
            self[name] = child
        else:
            super().__setattr__(name, child)


class ListNode:
    def __init__(self):
        self._parent = None
        self.selfref = None
        self._children = []

    def add_child(self, child):
        child._parent = self
        child.selfref = len(self._children)
        self._children.append(child)

    def add_children(self, *children):
        for child in children:
            self.add_child(child)

    def __setitem__(self, index, child):
        if index < 0: index += len(self._children)
        del self[index]
        if child:
            self._children[index] = child
            child._parent = self
            child.selfref = index

    def __getitem__(self, index):
        return self._children[index]

    def __delitem__(self, index):
        if index < 0: index += len(self._children)
        old = self._children[index]
        if old:
            old._parent = None
            old.selfref = None
        del self._children[index]
        for i, child in enumerate(self._children[index:]):
            child._parent = self
            child.selfref = index + i

    def __iter__(self):
        return iter(self._children)


class Number(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class BinaryOp(Node):
    def __init__(self, left, right):
        super().__init__()
        self.add_child('left', left)
        self.add_child('right', right)


class Sum(BinaryOp): pass
class Sub(BinaryOp): pass
class Mul(BinaryOp): pass
class Div(BinaryOp): pass
class Mod(BinaryOp): pass
class Eq(BinaryOp): pass
class Neq(BinaryOp): pass
class Gt(BinaryOp): pass
class Lt(BinaryOp): pass
class Geq(BinaryOp): pass
class Leq(BinaryOp): pass


class If(Node):
    def __init__(self, predicate, ifblock, elseblock=None):
        super().__init__()
        self.add_child('predicate', predicate)
        self.add_child('ifblock', ifblock)
        self.add_child('elseblock', elseblock)


class Print(Node):
    def __init__(self, value):
        super().__init__()
        self.add_child('value', value)


class Block(ListNode):
    def __init__(self, statements):
        super().__init__()
        self.add_children(*statements)


class Call(Node):
    def __init__(self, fn_name):
        super().__init__()
        self.fn_name = fn_name
        self.function = None


class Function(Node):
    def __init__(self, name, block):
        super().__init__()
        self.name = name
        self.add_child('block', block)


class VarDecl(Node):
    def __init__(self, name, typeref):
        super().__init__()
        self.name = name
        self.typeref = typeref


class Module(ListNode):
    def __init__(self):
        super().__init__()

    def append(self, function):
        self.add_child(function)
