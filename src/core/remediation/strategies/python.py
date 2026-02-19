import libcst as cst
import difflib
from typing import Optional, Union
from src.core.remediation.base import RemediationStrategy

class PythonRemediationStrategy(RemediationStrategy):
    """Base class for Python CST-based remediation strategies."""

    def get_diff(self, file_path: str, code: str, line: int) -> Optional[str]:
        modified_code = self.apply_fix(code, line)
        if modified_code is None:
            return None

        diff = difflib.unified_diff(
            code.splitlines(),
            modified_code.splitlines(),
            fromfile=file_path,
            tofile=file_path,
            lineterm=''
        )
        return '\n'.join(list(diff))

    def apply_fix(self, code: str, line: int) -> Optional[str]:
        try:
            source_tree = cst.parse_module(code)
            wrapper = cst.metadata.MetadataWrapper(source_tree)
            transformer = self.get_transformer(line)
            modified_tree = wrapper.visit(transformer)

            if not transformer.modified:
                return None

            return modified_tree.code

        except Exception as e:
            # Log specific errors if needed, but fail gracefully
            import traceback
            # traceback.print_exc()
            return None

    def get_transformer(self, line: int) -> cst.CSTTransformer:
        raise NotImplementedError

class ListAppendToComprehension(PythonRemediationStrategy):
    @property
    def rule_id(self) -> str:
        return 'inefficient_loop'

    @property
    def name(self) -> str:
        return 'List Comprehension'

    def get_suggestion(self) -> str:
        return "Convert loop to list comprehension for better performance."

    def get_transformer(self, line: int) -> cst.CSTTransformer:
        return ListAppendTransformer(line)

class ListAppendTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, target_line: int):
        self.target_line = target_line
        self.modified = False

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> Union[cst.For, cst.SimpleStatementLine]:
        pos = self.get_metadata(cst.metadata.PositionProvider, original_node).start
        if pos.line != self.target_line:
            return updated_node

        if len(updated_node.body.body) != 1:
            return updated_node

        statement = updated_node.body.body[0]
        if not isinstance(statement, cst.SimpleStatementLine):
            return updated_node

        if len(statement.body) != 1:
            return updated_node

        expr_stmt = statement.body[0]
        if not isinstance(expr_stmt, cst.Expr):
            return updated_node

        call = expr_stmt.value
        if not isinstance(call, cst.Call):
            return updated_node

        func = call.func
        if not isinstance(func, cst.Attribute):
            return updated_node

        if func.attr.value != 'append':
            return updated_node

        target_list = func.value
        if len(call.args) != 1:
            return updated_node
        element = call.args[0].value

        self.modified = True

        list_comp = cst.ListComp(
            elt=element,
            for_in=cst.CompFor(
                target=updated_node.target,
                iter=updated_node.iter,
                ifs=(),
                inner_for_in=None
            )
        )

        extend_call = cst.Call(
            func=cst.Attribute(value=target_list, attr=cst.Name("extend")),
            args=[cst.Arg(list_comp)]
        )

        return cst.SimpleStatementLine(
            body=[cst.Expr(value=extend_call)]
        )

class EnumerateTransformer(PythonRemediationStrategy):
    @property
    def rule_id(self) -> str:
        return 'range_len_usage'

    @property
    def name(self) -> str:
        return 'Use Enumerate'

    def get_suggestion(self) -> str:
        return "Use enumerate() instead of range(len()) for cleaner iteration."

    def get_transformer(self, line: int) -> cst.CSTTransformer:
        return RangeLenToEnumerateTransformer(line)

class RangeLenToEnumerateTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, target_line: int):
        self.target_line = target_line
        self.modified = False

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For:
        pos = self.get_metadata(cst.metadata.PositionProvider, original_node).start
        if pos.line != self.target_line:
            return updated_node

        iter_node = updated_node.iter
        if not isinstance(iter_node, cst.Call):
            return updated_node

        func = iter_node.func
        if not isinstance(func, cst.Name) or func.value != 'range':
            return updated_node

        if len(iter_node.args) != 1:
            return updated_node

        arg_val = iter_node.args[0].value
        if not isinstance(arg_val, cst.Call):
            return updated_node

        len_func = arg_val.func
        if not isinstance(len_func, cst.Name) or len_func.value != 'len':
            return updated_node

        if len(arg_val.args) != 1:
            return updated_node

        sequence = arg_val.args[0].value

        self.modified = True

        new_target = cst.Tuple(
            elements=[
                cst.Element(value=updated_node.target),
                cst.Element(value=cst.Name(value="_"))
            ]
        )

        new_iter = cst.Call(
            func=cst.Name(value="enumerate"),
            args=[cst.Arg(value=sequence)]
        )

        return updated_node.with_changes(target=new_target, iter=new_iter)


class UnnecessaryComprehensionTransformer(PythonRemediationStrategy):
    @property
    def rule_id(self) -> str:
        return 'unnecessary_comprehension'

    @property
    def name(self) -> str:
        return 'Remove Comprehension'

    def get_suggestion(self) -> str:
        return "Directly pass the iterable to list()/set() instead of using a comprehension."

    def get_transformer(self, line: int) -> cst.CSTTransformer:
        return RemoveComprehensionTransformer(line)

class RemoveComprehensionTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, target_line: int):
        self.target_line = target_line
        self.modified = False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        pos = self.get_metadata(cst.metadata.PositionProvider, original_node).start
        if pos.line != self.target_line:
            return updated_node

        func = updated_node.func
        if not isinstance(func, cst.Name) or func.value not in ('list', 'set', 'tuple'):
            return updated_node

        if len(updated_node.args) != 1:
            return updated_node

        arg_val = updated_node.args[0].value

        is_comp = False
        iterable = None

        if isinstance(arg_val, (cst.ListComp, cst.SetComp, cst.GeneratorExp)):
            # Check for simple identity mapping: [x for x in y]
            # No if conditions
            if arg_val.for_in.ifs:
                return updated_node

            # No nested loops
            if arg_val.for_in.inner_for_in:
                return updated_node

            elt = arg_val.elt
            target = arg_val.for_in.target

            # Check if elt and target are same Name
            if isinstance(elt, cst.Name) and isinstance(target, cst.Name):
                if elt.value == target.value:
                    iterable = arg_val.for_in.iter
                    is_comp = True

        if is_comp and iterable:
            self.modified = True
            return updated_node.with_changes(
                args=[cst.Arg(value=iterable)]
            )

        return updated_node
