class Number:
    def __init__(self, value):
        self.value = value


class BinaryOp:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __iter__(self):
        yield self.left
        yield self.right


class Sum(BinaryOp): pass
class Sub(BinaryOp): pass
class Eq(BinaryOp): pass


class If:
    def __init__(self, predicate, block):
        self.predicate = predicate
        self.block = block

    def __iter__(self):
        yield self.predicate
        yield self.block


class Print:
    def __init__(self, value):
        self.value = value


class Block:
    def __init__(self, statements):
        self.statements = statements

    def __iter__(self):
        return iter(self.statements)


class Call:
    def __init__(self, fn_name):
        self.fn_name = fn_name
        self.function = None


class Function:
    def __init__(self, name, block):
        self.name = name
        self.block = block

    def __iter__(self):
        yield self.block


class Module:
    def __init__(self, functions=[]):
        self.functions = functions

    def append(self, function):
        self.functions.append(function)

    def __iter__(self):
        return iter(self.functions)
