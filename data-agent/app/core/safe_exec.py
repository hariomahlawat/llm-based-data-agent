import ast
import builtins
from types import CodeType
from io import StringIO
import contextlib
from typing import Any, Dict, Tuple

ALLOWED_NODES = {
    ast.Module, ast.Expr, ast.Assign, ast.AugAssign,
    ast.Load, ast.Store, ast.Del,
    ast.Name, ast.Attribute, ast.Subscript,
    ast.Constant, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Call, ast.keyword, ast.List, ast.Tuple, ast.Dict, ast.Set,
    ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp,
    ast.Slice, ast.Index, ast.ExtSlice,
    ast.IfExp,
    ast.Return,
    ast.With, ast.withitem
}

ALLOWED_BUILTINS = {
    "len", "range", "min", "max", "sum", "sorted", "abs", "round", "enumerate",
    "zip", "any", "all", "map", "filter", "list", "dict", "set", "tuple"
}


class SafeVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        if type(node) not in ALLOWED_NODES:
            raise ValueError(f"Disallowed syntax: {type(node).__name__}")
        super().generic_visit(node)


def _analyze(code_str: str) -> ast.Module:
    tree = ast.parse(code_str, mode="exec")
    SafeVisitor().visit(tree)
    return tree


def run(code: str, context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    tree = _analyze(code)
    compiled: CodeType = compile(tree, filename="<safe_exec>", mode="exec")

    safe_builtins = {k: getattr(builtins, k) for k in ALLOWED_BUILTINS}

    safe_globals: Dict[str, Any] = {"__builtins__": safe_builtins}
    safe_globals.update(context)

    local_vars: Dict[str, Any] = {}
    stdout_buffer = StringIO()
    with contextlib.redirect_stdout(stdout_buffer):
        exec(compiled, safe_globals, local_vars)

    return local_vars, stdout_buffer.getvalue()


