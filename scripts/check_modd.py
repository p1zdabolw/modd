import ast
import io
import sys
import tokenize

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = sorted((ROOT / "modd").rglob("*.py")) + [ROOT / "build.py", ROOT / "modd.spec"]

failures = []
for path in TARGETS:
    source = path.read_text(encoding="utf-8")
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            failures.append(f"{path}:{token.start[0]}: comment token")
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        failures.append(f"{path}: syntax error: {error}")
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Pass):
            failures.append(f"{path}:{getattr(node, 'lineno', 0)}: pass statement")
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if node.value.value is Ellipsis:
                failures.append(f"{path}:{node.lineno}: ellipsis placeholder")
            if isinstance(node.value.value, str):
                failures.append(f"{path}:{node.lineno}: bare string (docstring)")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                failures.append(f"{path}:{node.lineno}: print() call")
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "set_trace"
                and isinstance(func.value, ast.Name)
                and func.value.id in ("pdb", "ipdb")
            ):
                failures.append(f"{path}:{node.lineno}: pdb.set_trace() call")

for failure in failures:
    print("FAIL", failure)
print("CHECKS", "OK" if not failures else f"{len(failures)} violations")
sys.exit(1 if failures else 0)
