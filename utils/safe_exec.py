"""
AST-based safe execution environment for LLM-generated matplotlib plot code.

Two-layer defence:
  1. Static AST validation  — rejects dangerous constructs before execution.
  2. Restricted globals      — exec() environment without dangerous names.
"""

import ast
import re
import io
import base64

# ---------------------------------------------------------------------------
# Blocklists
# ---------------------------------------------------------------------------

_BLOCKED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil",
    "builtins", "importlib", "pathlib", "ctypes",
    "multiprocessing", "threading", "signal",
    "pty", "cffi", "pickle", "shelve",
    "tempfile", "glob", "fnmatch",
}

_BLOCKED_BUILTINS = {
    "eval", "exec", "compile", "__import__",
    "open",
    "getattr", "setattr", "delattr", "hasattr",
    "vars", "dir", "globals", "locals",
    "breakpoint", "input",
    "memoryview", "bytearray",
}

_BLOCKED_DUNDER = re.compile(r"^__.*__$")

_BLOCKED_METHODS = {
    "system", "popen", "spawn", "call", "run",
    "check_output", "Popen",
}


# ---------------------------------------------------------------------------
# AST Validator
# ---------------------------------------------------------------------------

class _PlotCodeValidator(ast.NodeVisitor):
    """Raises ValueError on the first dangerous AST node found."""

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in _BLOCKED_MODULES:
                raise ValueError(f"Blocked import: '{alias.name}' is not allowed in plot code.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        root = module.split(".")[0]
        if root in _BLOCKED_MODULES:
            raise ValueError(f"Blocked import: 'from {module} import ...' is not allowed.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_BUILTINS:
                raise ValueError(f"Blocked call: '{node.func.id}()' is not allowed in plot code.")
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if _BLOCKED_DUNDER.match(attr):
                raise ValueError(f"Blocked dunder method call: '.{attr}()' is not allowed.")
            if attr in _BLOCKED_METHODS:
                raise ValueError(f"Blocked dangerous method call: '.{attr}()' is not allowed.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if _BLOCKED_DUNDER.match(node.attr):
            raise ValueError(f"Blocked dunder attribute access: '.{node.attr}' is not allowed.")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        raise ValueError("'global' statements are not allowed in plot code.")

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        raise ValueError("'nonlocal' statements are not allowed in plot code.")


# ---------------------------------------------------------------------------
# Restricted globals builder
# ---------------------------------------------------------------------------

def _build_restricted_globals() -> dict:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines
    import numpy as np
    import math
    import collections
    import itertools
    import functools

    safe_builtins = {
        "int": int, "float": float, "str": str, "bool": bool,
        "list": list, "dict": dict, "tuple": tuple, "set": set,
        "frozenset": frozenset, "bytes": bytes,
        "range": range, "enumerate": enumerate, "zip": zip,
        "map": map, "filter": filter, "reversed": reversed,
        "sorted": sorted, "len": len, "sum": sum,
        "min": min, "max": max, "abs": abs, "round": round,
        "pow": pow, "divmod": divmod,
        "isinstance": isinstance, "issubclass": issubclass, "type": type,
        "print": print,
        "repr": repr, "format": format,
        "any": any, "all": all,
        "next": next, "iter": iter,
        "id": id,
        "Exception": Exception, "ValueError": ValueError,
        "TypeError": TypeError, "IndexError": IndexError,
        "KeyError": KeyError, "StopIteration": StopIteration,
        "NotImplementedError": NotImplementedError,
        "RuntimeError": RuntimeError,
        "ZeroDivisionError": ZeroDivisionError,
        "AttributeError": AttributeError,
    }

    restricted = {
        "__builtins__": safe_builtins,
        "plt": plt,
        "matplotlib": matplotlib,
        "mpatches": mpatches,
        "mlines": mlines,
        "np": np,
        "numpy": np,
        "io": io,
        "base64": base64,
        "math": math,
        "re": re,
        "collections": collections,
        "itertools": itertools,
        "functools": functools,
    }

    try:
        import pandas as pd
        restricted["pd"] = pd
        restricted["pandas"] = pd
    except ImportError:
        pass

    return restricted


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_plot_code(code: str) -> None:
    """
    Parse `code` and walk its AST, raising ValueError if any dangerous
    construct is detected. Does not execute any code.
    """
    try:
        tree = ast.parse(code, mode="exec", filename="<plot_code>")
    except SyntaxError as exc:
        raise ValueError(f"Plot code has a syntax error: {exc}") from exc
    _PlotCodeValidator().visit(tree)


def safe_exec_plot_code(code_text: str, dpi: int = 100) -> str | None:
    """
    Extract Python code from ```python...``` fences, validate it via AST,
    then execute it in a restricted globals environment.

    Returns a base64-encoded JPEG string if a matplotlib figure was produced,
    or None otherwise.

    Raises:
        ValueError: if the code contains any disallowed construct or syntax error.
    """
    match = re.search(r"```python(.*?)```", code_text, re.DOTALL)
    code_clean = match.group(1).strip() if match else code_text.strip()

    if not code_clean:
        return None

    # Layer 1: AST validation
    validate_plot_code(code_clean)

    # Set up matplotlib
    import matplotlib.pyplot as plt
    plt.switch_backend("Agg")
    plt.close("all")
    plt.rcdefaults()

    # Layer 2: Restricted globals
    exec_globals = _build_restricted_globals()

    exec(code_clean, exec_globals)  # noqa: S102 — safe after AST validation

    if not plt.get_fignums():
        return None

    buf = io.BytesIO()
    plt.savefig(buf, format="jpeg", bbox_inches="tight", dpi=dpi)
    plt.close("all")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
