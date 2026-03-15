import ast
import textwrap
import re
from typing import List, Optional

# Regex patterns for JS/TS
# Pre-compiling regex for performance
JS_TS_RISKY_PATTERNS = [
    (re.compile(r'eval\s*\('), "Usage of 'eval' detected."),
    (re.compile(r'exec\s*\('), "Usage of 'exec' detected."),
    (re.compile(r'require\s*\(\s*[\'"]child_process[\'"]\s*\)'), "Import of 'child_process' detected."),
    (re.compile(r'require\s*\(\s*[\'"]fs[\'"]\s*\)'), "Import of 'fs' detected."),
    (re.compile(r'process\.exit'), "Usage of 'process.exit' detected."),
    (re.compile(r'spawn\s*\('), "Usage of 'spawn' detected."),
    (re.compile(r'setTimeout\s*\(\s*[\'"`]'), "Usage of 'setTimeout' with string detected (eval-like)."),
    (re.compile(r'setInterval\s*\(\s*[\'"`]'), "Usage of 'setInterval' with string detected (eval-like)."),
    (re.compile(r'document\.write'), "Usage of 'document.write' detected."),
    (re.compile(r'\.innerHTML\s*='), "Assignment to 'innerHTML' detected (XSS risk).")
]

RISKY_PYTHON_MODULES = {
    'os', 'subprocess', 'sys', 'shutil', 'socket',
    'requests', 'urllib', 'ftplib', 'pickle',
    'telnetlib', 'xmlrpc'
}

RISKY_PYTHON_FUNCTIONS = {
    'eval', 'exec', 'input', '__import__', 'compile', 'globals', 'locals', 'open'
}

RISKY_PYTHON_CALLS = {
    'os.system', 'os.popen', 'os.spawn', 'os.exec',
    'subprocess.call', 'subprocess.Popen', 'subprocess.run',
    'shutil.rmtree',
    'socket.socket',
    'urllib.request.urlopen'
}


def check_code_safety(code: str, language: str) -> List[str]:
    """
    Analyze code for potential security risks.
    Returns a list of warnings.
    """
    warnings = []

    # Normalize language
    lang = language.lower()

    if lang == 'python':
        warnings.extend(_check_python_safety(code))
    elif lang in ('javascript', 'typescript', 'js', 'ts'):
        warnings.extend(_check_js_ts_safety(code))

    return list(set(warnings))


def _check_python_safety(code: str) -> List[str]:
    warnings = []
    tree = _parse_python_code(code)

    if not tree:
        # Fallback: simple keyword check if parsing fails completely
        # This shouldn't happen often with the wrapper strategy
        warnings.append("Warning: Could not parse Python code. Running basic keyword check.")
        warnings.extend(_check_python_keywords(code))
        return warnings

    # AST Analysis
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_risky_module(alias.name):
                    warnings.append(f"Import of '{alias.name}' detected.")
        elif isinstance(node, ast.ImportFrom):
            if _is_risky_module(node.module):
                warnings.append(f"Import from '{node.module}' detected.")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if _is_risky_function(node.func.id):
                    warnings.append(f"Usage of '{node.func.id}' detected.")
            elif isinstance(node.func, ast.Attribute):
                # Check for things like subprocess.call
                # We can construct the full name if it's simple
                full_name = _get_attribute_name(node.func)
                if full_name and _is_risky_call(full_name):
                    warnings.append(f"Usage of '{full_name}' detected.")

    return warnings


def _check_python_keywords(code: str) -> List[str]:
    warnings = []
    risky = ['os.system', 'subprocess.call', 'eval(', 'exec(', '__import__', 'input(']
    for r in risky:
        if r in code:
            warnings.append(f"Potential risky pattern '{r}' detected (keyword check).")
    return warnings


def _parse_python_code(code: str) -> Optional[ast.AST]:
    """
    Try to parse Python code using multiple strategies to handle snippets.
    """
    # Strategy 1: Parse as is
    try:
        return ast.parse(code)
    except SyntaxError:
        pass

    # Strategy 2: Dedent
    try:
        dedented = textwrap.dedent(code)
        return ast.parse(dedented)
    except SyntaxError:
        pass

    # Strategy 3: Wrap in function (handles indentation issues)
    try:
        wrapped = "def _wrapper():\n" + textwrap.indent(code, "    ")
        return ast.parse(wrapped)
    except SyntaxError:
        pass

    return None


def _is_risky_module(name: Optional[str]) -> bool:
    if not name:
        return False
    return name.split('.')[0] in RISKY_PYTHON_MODULES


def _is_risky_function(name: str) -> bool:
    return name in RISKY_PYTHON_FUNCTIONS


def _get_attribute_name(node) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        value = _get_attribute_name(node.value)
        if value:
            return f"{value}.{node.attr}"
    return None


def _is_risky_call(name: str) -> bool:
    # Check if it starts with any risky prefix? No, exact match or simple containment usually enough.
    # But let's check strict match against known risky patterns or prefix match
    for pattern in RISKY_PYTHON_CALLS:
        if name.startswith(pattern):
            return True
    return False


def _check_js_ts_safety(code: str) -> List[str]:
    warnings = []
    for pattern, msg in JS_TS_RISKY_PATTERNS:
        if pattern.search(code):
            warnings.append(msg)
    return warnings
