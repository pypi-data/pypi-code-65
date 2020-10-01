#  MIT License
#
#  Copyright (c) 2020 Parakoopa
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from explorerscript.ssb_converting.compiler.utils import CompilerCtx, SsbLabelJumpBlueprint, does_op_end_control_flow
from explorerscript.ssb_converting.ssb_data_types import SsbOperation, SsbOpParam, SsbOpCode
from explorerscript.ssb_converting.ssb_special_ops import SsbLabel, SsbLabelJump, OPS_THAT_END_CONTROL_FLOW, OP_JUMP


def handler_is_for_statement(obj):
    return isinstance(obj, AbstractStatementCompileHandler)


class AbstractCompileHandler(ABC):
    """An abstract handler for compiling specific part of ExplorerScript source code"""
    def __init__(self, ctx, compiler_ctx: CompilerCtx):
        self.ctx = ctx
        self.compiler_ctx = compiler_ctx
        self._added_handlers: List[AbstractCompileHandler] = []

    @abstractmethod
    def collect(self) -> any:
        """Collect the result of this handler. The returned value can vary greatly based on the handler!"""
        pass

    @abstractmethod
    def add(self, obj: any):
        """
        Add a sub-object to this handler. What is accepted is based on the handler! If something isn't
        supported, a ValueError should be raised.
        To streamline the error process, _raise_add_error can be used.
        """
        pass

    def _raise_add_error(self, obj: any):
        raise ValueError(f"Compiler logic error: {self.__class__} does not support {type(obj)} handlers.")

    def _generate_operation(self, op_name: str, params: List[SsbOpParam]) -> SsbOperation:
        """Generates an operation, increases the counter and updates the source map"""
        return self._register_operation(SsbOperation(
            self.compiler_ctx.counter_ops(),
            SsbOpCode(-1, op_name),
            params
        ))

    def _generate_jump_operation(self, op_name: str, params: List[SsbOpParam], label: Optional[SsbLabel], none_allowed=False):
        if not none_allowed:
            assert label is not None
        return SsbLabelJump(
            self._generate_operation(op_name, params), label
        )

    def _register_operation(self, op: SsbOperation) -> SsbOperation:
        """
        Register an operation. This updates the source map (but doesn't increase the counter),
        so it's supposed to be done in collect()!
        """
        self.compiler_ctx.source_map_builder.add_opcode(
            # Antlr line ids are 1-indexed.
            self.compiler_ctx.counter_ops.count, self.ctx.start.line - 1, self.ctx.start.column
        )
        return op


class AbstractStatementCompileHandler(AbstractCompileHandler, ABC):
    """A compile handler that generates a list of binary opcodes."""
    @abstractmethod
    def collect(self) -> List[SsbOperation]:
        """Collect a list of operations generated by this handler."""
        pass


class AbstractAssignmentCompileHandler(AbstractStatementCompileHandler, ABC):
    pass


class AbstractBlockCompileHandler(AbstractStatementCompileHandler, ABC):
    """A handler that manages a sub-block of operations and generates one or multiple header operations"""
    def __init__(self, ctx, compiler_ctx: CompilerCtx):
        super().__init__(ctx, compiler_ctx)
        # The added handlers are the opcodes in the block
        # A list of headers that jump to the block.
        self._header_jump_blueprints: List[SsbLabelJumpBlueprint] = []
        # The processed jumps
        self.processed_header_jumps: List[SsbLabelJump] = []
        self._added_handlers: List[AbstractStatementCompileHandler] = []
        self.start_label: Optional[SsbLabel] = None
        self.end_label: Optional[SsbLabel] = None

    def _process_block(self, insert_the_jump_if_needed=True) -> List[SsbOperation]:
        """
        This processes the sub-block and returns the generated sub-block opcodes.
        - Opcodes are collected (warning: opcode indexing! Make sure you allocated index numbers for the header ops!)
        - From the header jump blueprints, jump opcodes are created [only applies if there are some!]
            - If the sub-block only has one single label jump, it's removed and the target
              of the headers is changed to the target of that jump
            - Otherwise the jump is set to the offset id of the first opcode in the sub-block.
        - If insert_the_jump_if_needed:
            - If the last op of a block does not end the control flow, a label jump is inserted.
                - The label is set to None and is expected to be replaced with the real end label of
                  the if (see _update_last_jump_to_end_label).

        After this the generated header opcodes can be retrieved using get_processed_header_jumps()

        The returned list is guaranteed to have one entry: the end label (next opcode outside this block).
        It usually also has a start label (if the only-one-jump case didn't happen).
        """
        ops: List[SsbOperation] = []

        for h in self._added_handlers:
            ops += h.collect()

        self.end_label = SsbLabel(
            self.compiler_ctx.counter_labels(), -1, f'{self.__class__.__name__} block end label'
        )

        if len(self._header_jump_blueprints) > 0 and len(ops) == 1 \
                and isinstance(ops[0], SsbLabelJump) and ops[0].root.op_code.name == OP_JUMP:
            # Just has a jump, insert that into the headers instead
            for hjb in self._header_jump_blueprints:
                self.processed_header_jumps.append(hjb.build_for(ops[0].label))
            self.start_label = ops[0].label
            return [self.end_label]  # in this case we don't actually have any operations to write

        if insert_the_jump_if_needed and (len(ops) < 1 or not does_op_end_control_flow(ops[-1], ops[-2] if len(ops) > 1 else None)):
            # insert the end label jump
            ops.append(self._generate_empty_jump())

        # Generate the start and end label for this block
        self.start_label = SsbLabel(
            self.compiler_ctx.counter_labels(), -1, f'{self.__class__.__name__} block start label'
        )
        ops.insert(0, self.start_label)
        ops.append(self.end_label)
        # Update headers to jump to/over the block
        for hjb in self._header_jump_blueprints:
            if hjb.jump_is_positive:
                self.processed_header_jumps.append(hjb.build_for(self.start_label))
            else:
                self.processed_header_jumps.append(hjb.build_for(self.end_label))

        return ops

    def _generate_empty_jump(self) -> SsbLabelJump:
        """Generate a new empty jump operation"""
        return self._generate_jump_operation(OP_JUMP, [], None, True)

    def get_processed_header_jumps(self):
        return self.processed_header_jumps

    def set_processed_header_jumps(self, val: List[SsbLabelJump]):
        self.processed_header_jumps = val

    def get_start_label(self):
        return self.start_label


class AbstractLoopBlockCompileHandler(AbstractBlockCompileHandler, ABC):
    def __init__(self, ctx, compiler_ctx: CompilerCtx):
        super().__init__(ctx, compiler_ctx)
        self._start_label = SsbLabel(
            self.compiler_ctx.counter_labels(), -1, f'{self.__class__.__name__} outer start label'
        )
        self._end_label = SsbLabel(
            self.compiler_ctx.counter_labels(), -1, f'{self.__class__.__name__} outer end label'
        )

    def continue_loop(self) -> SsbOperation:
        return self._generate_jump_operation(OP_JUMP, [], self._start_label)

    def break_loop(self) -> SsbOperation:
        return self._generate_jump_operation(OP_JUMP, [], self._end_label)


class AbstractFuncdefCompileHandler(AbstractCompileHandler, ABC):
    """An abstract handler for funcdefs."""
    def add(self, obj: any):
        if handler_is_for_statement(obj):
            self._added_handlers.append(obj)
            return
        self._raise_add_error(obj)

    def collect_ops(self) -> List[SsbOperation]:
        """Collects all operations in a routine."""
        ops = []
        for h in self._added_handlers:
            ops_of_h = h.collect()
            assert isinstance(ops_of_h, list) and (len(ops_of_h) == 0 or isinstance(ops_of_h[0], SsbOperation))
            ops += ops_of_h
        return ops

    @abstractmethod
    def get_new_routine_id(self, old_id: int) -> int:
        pass
