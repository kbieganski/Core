from llvmlite import ir, binding
from .visitor import *
from .ast import *


class CodeGen(Visitor):
    def __init__(self):
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()
        self.fmtstr = None
        self._create_execution_engine()

    def _create_execution_engine(self):
        """
        Create an ExecutionEngine suitable for JIT code generation on
        the host CPU.  The engine is reusable for an arbitrary number of
        modules.
        """
        target = self.binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module
        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        self.engine = engine

    def compile_ir(self):
        """
        Compile the LLVM IR string with the given engine.
        The compiled module object is returned.
        """
        # Create a LLVM module object from the IR
        llvm_ir = str(self.module)
        print(llvm_ir)
        mod = self.binding.parse_assembly(llvm_ir)
        mod.verify()
        # Now add the module and make sure it is ready for execution
        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    def save_ir(self, filename):
        with open(filename, 'w') as output_file:
            output_file.write(str(self.module))

    @visitor(Number)
    def visit(self, node):
        return ir.Constant(ir.IntType(8), int(node.value))

    @visitor(Sum)
    def visit(self, node):
        return self.builder.add(self.visit(node.left), self.visit(node.right))

    @visitor(Sub)
    def visit(self, node):
        return self.builder.sub(self.visit(node.left), self.visit(node.right))

    @visitor(Mul)
    def visit(self, node):
        return self.builder.mul(self.visit(node.left), self.visit(node.right))

    @visitor(Div)
    def visit(self, node):
        return self.builder.sdiv(self.visit(node.left), self.visit(node.right))

    @visitor(Mod)
    def visit(self, node):
        return self.builder.srem(self.visit(node.left), self.visit(node.right))

    @visitor(Eq)
    def visit(self, node):
        return self.builder.icmp_signed('==', self.visit(node.left), self.visit(node.right))

    @visitor(Neq)
    def visit(self, node):
        return self.builder.icmp_signed('!=', self.visit(node.left), self.visit(node.right))

    @visitor(Gt)
    def visit(self, node):
        return self.builder.icmp_signed('>', self.visit(node.left), self.visit(node.right))

    @visitor(Lt)
    def visit(self, node):
        return self.builder.icmp_signed('<', self.visit(node.left), self.visit(node.right))

    @visitor(Geq)
    def visit(self, node):
        return self.builder.icmp_signed('>=', self.visit(node.left), self.visit(node.right))

    @visitor(Leq)
    def visit(self, node):
        return self.builder.icmp_signed('<=', self.visit(node.left), self.visit(node.right))

    @visitor(Print)
    def visit(self, node):
        value = self.visit(node.value)

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        if not self.fmtstr:
            fmt = "%i \n\0"
            c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                                bytearray(fmt.encode("utf8")))
            self.fmtstr = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
            self.fmtstr.linkage = 'internal'
            self.fmtstr.global_constant = True
            self.fmtstr.initializer = c_fmt
        fmt_arg = self.builder.bitcast(self.fmtstr, voidptr_ty)

        # Call Print Function
        self.builder.call(self.printf, [fmt_arg, value])

    @visitor(If)
    def visit(self, node):
        pred = self.visit(node.predicate)
        with self.builder.if_then(pred) as then:
            self.visit(node.ifblock)

    @visitor(Call)
    def visit(self, node):
        self.builder.call(node.function.function, [])

    @visitor(Function)
    def visit(self, node):
        func_type = ir.FunctionType(ir.VoidType(), [], False)
        function = ir.Function(self.module, func_type, name=node.name)
        block = function.append_basic_block()
        self.builder = ir.IRBuilder(block)
        self.visit(node.block)
        self.builder.ret_void()
        node.function = function

    @visitor(Module)
    def visit(self, node):
        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        self.iterate(node)
