import ast
import builtins
import contextlib
import multiprocessing as mp
import signal
from io import StringIO
from types import CodeType
from typing import Any, Dict, Tuple

from app.core.config import settings

try:  # resource is Unix only
    import resource
except Exception:  # pragma: no cover - windows
    resource = None  # type: ignore

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


def _worker(code_str: str, context: Dict[str, Any], q: mp.Queue, timeout: int) -> None:
    """Execute code in a separate process and put results on queue."""
    tree = _analyze(code_str)
    compiled: CodeType = compile(tree, filename="<safe_exec>", mode="exec")

    if resource is not None:
        # limit CPU seconds roughly equal to timeout
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        # limit address space to configured memory in bytes
        max_mem = settings.safe_exec_mem_mb * 1_048_576
        try:
            resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))
        except ValueError:
            pass

    def _alarm_handler(signum, frame):  # pragma: no cover - relies on OS
        raise TimeoutError("Time limit exceeded")

    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(timeout)

    safe_builtins = {k: getattr(builtins, k) for k in ALLOWED_BUILTINS}
    safe_globals: Dict[str, Any] = {"__builtins__": safe_builtins}
    safe_globals.update(context)

    local_vars: Dict[str, Any] = {}
    stdout_buffer = StringIO()
    with contextlib.redirect_stdout(stdout_buffer):
        exec(compiled, safe_globals, local_vars)

    q.put((local_vars, stdout_buffer.getvalue()))


def run(code: str, context: Dict[str, Any], timeout: int = 5) -> Tuple[Dict[str, Any], str]:
    """Safely execute code with a time limit."""
    ctx = mp.get_context("spawn")
    q: mp.Queue = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(code, context, q, timeout))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        raise TimeoutError("Execution timed out")
    if not q.empty():
        return q.get()
    return {}, ""


