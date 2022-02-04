from llvmlite import ir, binding
from .visitor import *
from .ast import *


class CodegenGlobal(Visitor):
    @visitor(VariableList)
    def visit(self, node):
        self.iterate(node)
        node.ir = [var.type.ir for var in node]

    @visitor(Reference)
    def visit(self, node):
        node.ir = node.target.ir

    @visitor(Type)
    def visit(self, node):
        match node.name:
            case 'int8': node.ir = ir.IntType(8)
            case 'int16': node.ir = ir.IntType(16)
            case 'int32': node.ir = ir.IntType(32)
            case 'int64': node.ir = ir.IntType(64)
        #elif node.name == 'fn()':
        #    node.ir = ir.FunctionType(ir.VoidType(), node.parameters.ir, False)

    @visitor(Function)
    def visit(self, node):
        self.visit(node.parameters)
        func_type = ir.FunctionType(ir.VoidType(), node.parameters.ir, False)
        function = ir.Function(self.module, func_type, name=node.name)
        for i, arg in enumerate(function.args):
            arg.name = node.parameters[i].name
            node.parameters[i].ir = arg
        node.ir = function

    @visitor(Module)
    def visit(self, node):
        self.module = ir.Module(name="main_module")
        self.module.triple = binding.get_default_triple()

        printf_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        node.printf = ir.Function(self.module, printf_ty, name="printf")

        fmt = "%i \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        node.fmtstr = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
        node.fmtstr.linkage = 'internal'
        node.fmtstr.global_constant = True
        node.fmtstr.initializer = c_fmt

        self.iterate(node)
        node.module = self.module


class CodegenLocal(Visitor):
    def __init__(self):
        self.fmtstr = None

    @visitor(Number)
    def visit(self, node):
        self.iterate(node)
        node.ir = ir.Constant(node.type.ir, int(node.value))

    @visitor(Sum)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.add(node.left.ir, node.right.ir)

    @visitor(Sub)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.sub(node.left.ir, node.right.ir)

    @visitor(Mul)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.mul(node.left.ir, node.right.ir)

    @visitor(Div)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.sdiv(node.left.ir, node.right.ir)

    @visitor(Mod)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.srem(node.left.ir, node.right.ir)

    @visitor(Eq)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('==', node.left.ir, node.right.ir)

    @visitor(Neq)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('!=', node.left.ir, node.right.ir)

    @visitor(Gt)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('>', node.left.ir, node.right.ir)

    @visitor(Lt)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('<', node.left.ir, node.right.ir)

    @visitor(Geq)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('>=', node.left.ir, node.right.ir)

    @visitor(Leq)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.icmp_signed('<=', node.left.ir, node.right.ir)

    @visitor(Print)
    def visit(self, node):
        self.iterate(node)
        fmt_arg = self.builder.bitcast(self.fmtstr, ir.IntType(8).as_pointer())
        self.builder.call(self.printf, [fmt_arg, node.value.ir])

    @visitor(If)
    def visit(self, node):
        self.visit(node.predicate)
        with self.builder.if_then(node.predicate.ir) as then:
            self.visit(node.ifblock)

    @visitor(Call)
    def visit(self, node):
        self.iterate(node)
        self.builder.call(node.function.ir, node.arguments.ir)

    @visitor(Cast)
    def visit(self, node):
        self.iterate(node)
        print(node.type.ir.width)
        if node.type.ir.width < node.argument.ir.type.width:
            node.ir = self.builder.trunc(node.argument.ir, node.type.ir)
        else:
            node.ir = self.builder.sext(node.argument.ir, node.type.ir)

    @visitor(ArgumentList)
    def visit(self, node):
        self.iterate(node)
        r = [expr.ir for expr in node]
        for i in range(len(r)): # TODO find a better way to do this
            if isinstance(r[i], ir.instructions.AllocaInstr):
                r[i] = self.builder.load(r[i])
        node.ir = r

    @visitor(Variable)
    def visit(self, node):
        self.iterate(node)
        node.ir = self.builder.alloca(node.type.ir, name=node.name)

    @visitor(Assignment)
    def visit(self, node):
        self.iterate(node)
        self.builder.store(node.rhs.ir, node.lhs.ir)

    @visitor(Reference)
    def visit(self, node):
        node.ir = node.target.ir

    @visitor(Function)
    def visit(self, node):
        if not node.block: return
        block = node.ir.append_basic_block()
        self.builder = ir.IRBuilder(block)
        self.visit(node.block)
        self.builder.ret_void()

    @visitor(Module)
    def visit(self, node):
        self.module = node.module
        self.printf = node.printf
        self.fmtstr = node.fmtstr
        self.iterate(node)
        return node.module


def codegen(root):
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = binding.parse_assembly("")
    engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    CodegenGlobal().visit(root)
    module = CodegenLocal().visit(root)
    llvm_ir = str(module)
    print(llvm_ir)
    mod = binding.parse_assembly(llvm_ir)
    mod.verify()
    engine.add_module(mod)
    engine.finalize_object()
    engine.run_static_constructors()
    mod.engine = engine # so engine doesn't get collected. TODO: make this cleaner
    return mod
