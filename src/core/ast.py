class Node:
    def __init__(self):
        self._parent = None
        self.selfref = None

    def delete(self):
        self.replace(None)

    def replace(self, *new):
        if self._parent:
            parent = self._parent
            selfref = self.selfref
            parent[selfref] = new[0]
            for i in range(1, len(new)):
                parent.add_child(selfref + i, new[i])
        return self

    def unlink(self):
        return self.replace(None)

    def next(self):
        if self._parent:
            try:
                return self._parent[self.selfref + 1]
            except TypeError:
                pass

    def __iter__(self):
        return iter([])


class DictNode(Node):
    def __init__(self):
        super().__init__()
        self._children = {}

    def add_child(self, name, node):
        self._children[name] = None
        self[name] = node

    def __setitem__(self, name, child):
        del self[name]
        if child:
            child.unlink()
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


class ListNode(Node):
    def __init__(self, children=[]):
        super().__init__()
        self._children = []
        self.add_children(*children)

    def add_child(self, index, child=None):
        if not child:
            index, child = child, index
        child.unlink()
        child._parent = self
        if index:
            self._children.insert(index, child)
            for i, child in enumerate(self._children[index:]):
                child.selfref = index + i
        else:
            child.selfref = len(self._children)
            self._children.append(child)

    def add_children(self, *children):
        for child in children:
            self.add_child(child)

    def __setitem__(self, index, child):
        if index < 0: index += len(self._children)
        if child:
            self._children[index]._parent = None
            self._children[index].selfref = None
            self._children[index] = child
            child._parent = self
            child.selfref = index
        else:
            del self[index]

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
            child.selfref = index + i

    def __iter__(self):
        return iter(self._children)


class Number(DictNode):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.add_child('type', None)


class BinaryOp(DictNode):
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


class If(DictNode):
    def __init__(self, predicate, ifblock, elseblock=None):
        super().__init__()
        self.add_child('predicate', predicate)
        self.add_child('ifblock', ifblock)
        self.add_child('elseblock', elseblock)


class Print(DictNode):
    def __init__(self, value):
        super().__init__()
        self.add_child('value', value)


class Block(ListNode):
    def __init__(self, statements):
        super().__init__()
        self.add_children(*statements)


class ArgumentList(ListNode):
    def __init__(self, expressions):
        super().__init__()
        self.add_children(*expressions)


class VariableList(ListNode):
    def __init__(self, parameters):
        super().__init__()
        self.add_children(*parameters)
        self.count = len(parameters)


class Call(DictNode):
    def __init__(self, function, arguments):
        super().__init__()
        self.add_child('function', function)
        self.add_child('arguments', arguments)


class Cast(DictNode):
    def __init__(self, type, argument):
        super().__init__()
        self.add_child('type', type)
        self.add_child('argument', argument)


class Function(DictNode):
    def __init__(self, name, block, parameters=VariableList([])):
        super().__init__()
        self.name = name
        self.add_child('parameters', parameters)
        self.add_child('block', block)


class FuncDecl(DictNode):
    def __init__(self, name, block, parameters=VariableList([])):
        super().__init__()
        self.name = name
        self.add_child('parameters', parameters)
        self.add_child('block', block)



class Assignment(DictNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.add_child('lhs', lhs)
        self.add_child('rhs', rhs)


class VarDecl(DictNode):
    def __init__(self, name, expression):
        super().__init__()
        self.name = name
        self.add_child('expression', expression)


class Variable(DictNode):
    def __init__(self, name, type=None):
        super().__init__()
        self.name = name
        self.add_child('type', type)


class Type(DictNode):
    def __init__(self, name):
        super().__init__()
        self.name = name


class BasicType(DictNode):
    def __init__(self, name):
        super().__init__()
        self.name = name


class FunctionType(DictNode):
    def __init__(self, name, arg_types, ret_type):
        super().__init__()
        self.name = name
        self.arg_types = arg_types
        self.ret_type = ret_type


class Scope(ListNode):
    def __init__(self, children):
        super().__init__()
        self.add_children(*children)
        self.names = {}
        self.parent_scope = None

    def resolve(self, name):
        try:
            return self.names[name]
        except KeyError as e:
            if self.parent_scope:
                return self.parent_scope.resolve(name)
            raise e

    def register(self, name, node):
        self.names[name] = node


class Reference(DictNode):
    def __init__(self, ref):
        super().__init__()
        if isinstance(ref, str):
            self.name = ref
            self.target = None
        else:
            self.target = ref
            self.name = self.target.name
        self.type = None


class Module(ListNode):
    def __init__(self):
        super().__init__()
