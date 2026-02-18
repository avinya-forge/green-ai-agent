"""
Python-specific detection strategies for green software violations.
"""

import ast
from typing import List, Dict

class PythonViolationDetector(ast.NodeVisitor):
    """AST visitor to detect green software violations in Python code."""
    
    IO_PATTERNS = {'open', 'read', 'write', 'requests', 'urlopen'}
    REDUNDANT_FUNCS = {'len', 'range', 're.compile', 'datetime.now', 'time.time'}
    BLOCKING_IO = {'requests.get', 'urlopen', 'time.sleep'}

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []
        self.current_depth = 0
        self.in_loop = False
        self.in_async = False
        self.current_function = None
        self.unused_variables = {}
        self.used_variables = set()
        self.imports = {}
        self.var_types = {}
        
    def detect_all(self) -> List[Dict]:
        """Run all detectors and return violations."""
        try:
            tree = ast.parse(self.content)
            self.visit(tree)
            
            # Post-processing for unused detection
            self._detect_unused_variables()
            self._detect_unused_imports()
            
        except SyntaxError:
            pass
        
        return self.violations
    
    def visit_For(self, node: ast.For) -> None:
        """Detect nested loops and I/O in loops."""
        self._check_empty_block(node, 'for loop')
        self.current_depth += 1
        
        # Rule: Excessive nesting depth (O(n^2) or worse)
        if self.current_depth >= 2:
            severity = 'critical' if self.current_depth >= 3 else 'major'
            self.violations.append({
                'id': 'no_n2_algorithms',
                'line': node.lineno,
                'severity': severity,
                'message': f'Nesting depth {self.current_depth}: O(n^{self.current_depth}) complexity detected.',
                'pattern_match': 'nested_for_loop'
            })

        # Rule: Inefficient Loop (range(len))
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call):
                arg_call = node.iter.args[0]
                if isinstance(arg_call.func, ast.Name) and arg_call.func.id == 'len':
                    self.violations.append({
                        'id': 'inefficient_loop',
                        'line': node.lineno,
                        'severity': 'major',
                        'message': 'Using range(len(sequence)) is inefficient. Use enumerate() or zip().',
                        'pattern_match': 'range_len'
                    })

        # Rule: Inefficient Dictionary Iteration (.keys())
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == 'keys':
            self.violations.append({
                'id': 'inefficient_dictionary_iteration',
                'line': node.lineno,
                'severity': 'minor',
                'message': 'Iterating over .keys() is redundant. Iterate over the dictionary directly.',
                'pattern_match': 'dict_keys_iter'
            })
        
        # Rule: Inefficient Lookup (item in list in loop)
        self._check_inefficient_lookups(node)
        
        # Check for I/O and redundant computations in loop
        prev_in_loop = self.in_loop
        self.in_loop = True
        self._check_io_in_loop(node)
        self._check_unnecessary_computation(node)
        
        self.generic_visit(node)
        self.in_loop = prev_in_loop
        self.current_depth -= 1
    
    def visit_While(self, node: ast.While) -> None:
        """Detect while loop violations."""
        self._check_empty_block(node, 'while loop')
        self.current_depth += 1
        
        is_infinite = False
        test = node.test
        if isinstance(test, ast.Constant) and test.value is True:
            is_infinite = True
        elif isinstance(test, ast.Name) and test.id == 'True':
            is_infinite = True
            
        if is_infinite:
             is_infinite = True
        
        if is_infinite:
             self.violations.append({
                'id': 'no_infinite_loops',
                'line': node.lineno,
                'severity': 'critical',
                'message': 'Infinite loop detected (while True). Ensure break condition exists.',
                'pattern_match': 'infinite_while'
            })

        if self.current_depth >= 3:
            self.violations.append({
                'id': 'excessive_nesting_depth',
                'line': node.lineno,
                'severity': 'critical',
                'message': f'Nesting depth {self.current_depth}: O(n^{self.current_depth}) complexity detected.',
                'pattern_match': 'nested_while_loop'
            })
        
        prev_in_loop = self.in_loop
        self.in_loop = True
        self._check_io_in_loop(node)
        self._check_unnecessary_computation(node)
        
        self.generic_visit(node)
        self.in_loop = prev_in_loop
        self.current_depth -= 1
    
    def visit_If(self, node: ast.If) -> None:
        """Track if statements for complexity."""
        self._check_empty_block(node, 'if statement')
        self.current_depth += 1
        self.generic_visit(node)
        self.current_depth -= 1
    
    def _check_io_in_loop(self, loop_node) -> None:
        """Check if loop contains I/O operations."""
        io_patterns = ['open', 'read', 'write', 'requests', 'urlopen']
        
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in io_patterns:
                        self.violations.append({
                            'id': 'io_in_loop',
                            'line': child.lineno,
                            'severity': 'critical',
                            'message': f'I/O operation "{child.func.id}()" in loop. Each call costs 100-1000x more energy.',
                            'pattern_match': 'io_operation_in_loop'
                        })
    
    def _check_unnecessary_computation(self, loop_node) -> None:
        """
        Check for redundant computations in loop that could be moved outside.
        E.g., len(s), range(n) if n is constant, re.compile, etc.
        """
        redundant_funcs = ['len', 'range', 're.compile', 'datetime.now', 'time.time', 'count']
        
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                func_name = None
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    # Handle re.compile or similar
                    if isinstance(child.func.value, ast.Name):
                        func_name = f"{child.func.value.id}.{child.func.attr}"

                    # Also match .count() regardless of caller
                    if child.func.attr == 'count':
                        func_name = 'count'
                
                if func_name in redundant_funcs:
                    # Heuristic: Check if arguments are actually dependent on loop variables
                    # For simplicity in this version, we flag common ones that are often static
                    self.violations.append({
                        'id': 'unnecessary_computation',
                        'line': child.lineno,
                        'severity': 'critical',
                        'message': f'Redundant computation "{func_name}()" in loop. Move outside for O(1) impact.',
                        'pattern_match': 'computation_outside_loop'
                    })
    
    def _check_inefficient_lookups(self, loop_node) -> None:
        """Check for membership tests on lists inside loops (O(n) vs O(1))."""
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Compare):
                for op in child.ops:
                    if isinstance(op, (ast.In, ast.NotIn)):
                        # If the right side is a Name, it might be a list
                        # This is a heuristic - in real tool we'd track types
                        if isinstance(child.comparators[0], ast.Name):
                            var_name = child.comparators[0].id
                            # If we know it's efficient, skip violation
                            if self.var_types.get(var_name) == 'efficient':
                                continue

                            self.violations.append({
                                'id': 'inefficient_lookup',
                                'line': child.lineno,
                                'severity': 'medium',
                                'message': f'Membership test on "{var_name}" inside loop. If it is a list, consider converting to a set for O(1) lookup.',
                                'pattern_match': 'list_lookup_loop'
                            })
    
    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Detect string concatenation in loops."""
        # Simplified handling moved to visit_Assign for proper accumulation detection
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Detect string concatenation with += in loops."""
        if self.in_loop and isinstance(node.op, ast.Add):
            is_string_op = False
            # Check target (LHS)
            if isinstance(node.target, ast.Name) and self.var_types.get(node.target.id) == 'str':
                is_string_op = True

            # Check value (RHS)
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                is_string_op = True
            elif isinstance(node.value, ast.Name) and self.var_types.get(node.value.id) == 'str':
                is_string_op = True

            if is_string_op:
                 self.violations.append({
                    'id': 'string_concatenation_in_loop',
                    'line': node.lineno,
                    'severity': 'medium',
                    'message': 'String concatenation in loop creates O(n²) memory allocations. Use list.append() and "".join().',
                    'pattern_match': 'string_concat_loop'
                })
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls for I/O and performance issues."""
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.used_variables.add(func_name)
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            func_name = f"{node.func.value.id}.{node.func.attr}"

        if func_name:
            # Rule: Blocking I/O
            blocking_io = ['requests.get', 'urlopen', 'time.sleep']
            if func_name in blocking_io or any(func_name.endswith(f'.{b}') for b in blocking_io):
                self.violations.append({
                    'id': 'blocking_io',
                    'line': node.lineno,
                    'severity': 'high',
                    'message': f'Blocking I/O operation "{func_name}()". Consider async/await.',
                    'pattern_match': 'sync_io'
                })
            
            # Rule: Blocking I/O in Async
            if self.in_async:
                # time.sleep, requests.*, open
                blocking_calls = ['time.sleep', 'requests', 'open']
                # Note: 'requests' covers all methods if we match prefix or exact

                is_blocking_in_async = False
                if func_name == 'time.sleep':
                    is_blocking_in_async = True
                elif func_name == 'open':
                    is_blocking_in_async = True
                elif func_name.startswith('requests.'):
                    is_blocking_in_async = True
                elif func_name == 'requests': # if called directly? rare but possible
                     is_blocking_in_async = True

                if is_blocking_in_async:
                    self.violations.append({
                        'id': 'blocking_io_in_async',
                        'line': node.lineno,
                        'severity': 'critical',
                        'message': f'Blocking I/O "{func_name}()" inside async function. Blocks the event loop. Use aiohttp/aiofiles or run_in_executor.',
                        'pattern_match': 'async_blocking_io'
                    })

            # Rule: Resource might leak (proper_resource_cleanup)
            if func_name == 'open' and not self._is_in_context_manager(node):
                self.violations.append({
                    'id': 'proper_resource_cleanup',
                    'line': node.lineno,
                    'severity': 'high',
                    'message': 'File opened without context manager. Use "with open()" to ensure closure.',
                    'pattern_match': 'file_not_closed'
                })

            # Rule: Excessive Logging
            if func_name == 'print':
                self.violations.append({
                    'id': 'excessive_logging',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': 'Usage of "print" detected. Use logging module or remove in production.',
                    'pattern_match': 'print_usage'
                })

        # Rule: Excessive Logging (Logger methods)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['debug', 'info', 'log']:
             # Heuristic: check if called on something like 'args.logger' or 'logging' or 'logger'
             if isinstance(node.func.value, ast.Name) and node.func.value.id in ['logger', 'logging']:
                  self.violations.append({
                    'id': 'excessive_logging',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': f'Excessive logging call "{node.func.attr}". Verify log levels.',
                    'pattern_match': 'logging_call'
                })

        # Rule: Heavy object copying
        if (isinstance(node.func, ast.Attribute) and node.func.attr == 'deepcopy') or (func_name == 'deepcopy'):
            self.violations.append({
                'id': 'heavy_object_copy',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Usage of deepcopy detected. This is computationally expensive.',
                'pattern_match': 'deepcopy'
            })

        # Rule: Process Spawning
        call_s = ast.dump(node.func) # Simplified string check
        if 'subprocess' in call_s or 'os.system' in call_s or 'popen' in call_s.lower():
             # Basic filter to avoid false positives if variable names match
             is_process = False
             if isinstance(node.func, ast.Attribute):
                 if node.func.attr in ['run', 'Popen', 'system', 'spawn']:
                     is_process = True
             elif func_name in ['system', 'popen', 'spawn']:
                 is_process = True
            
             if is_process:
                self.violations.append({
                    'id': 'process_spawning',
                    'line': node.lineno,
                    'severity': 'critical',
                    'message': 'Process spawning detected. High OS overhead.',
                    'pattern_match': 'process_spawn'
                })

        # Rule: Inefficient file reading (Attribute call)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'readlines':
            self.violations.append({
                'id': 'inefficient_file_read',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Using readlines() reads entire file into memory. Iterate file object instead.',
                'pattern_match': 'readlines'
            })

        # Rule: Pandas iterrows
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'iterrows':
            self.violations.append({
                'id': 'pandas_iterrows',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Using iterrows() is slow. Use vectorization or apply().',
                'pattern_match': 'iterrows'
            })

        # Rule: Any/All List Comprehension
        if isinstance(node.func, ast.Name) and node.func.id in ['any', 'all']:
            if node.args and isinstance(node.args[0], ast.ListComp):
                 self.violations.append({
                    'id': 'any_all_list_comprehension',
                    'line': node.lineno,
                    'severity': 'major',
                    'message': f'Using list comprehension with {node.func.id}(). Use generator expression for lazy evaluation.',
                    'pattern_match': 'any_all_list_comp'
                })

        # Rule: Unnecessary List in Generator (sum/max/min)
        if isinstance(node.func, ast.Name) and node.func.id in ['sum', 'max', 'min']:
             if node.args and isinstance(node.args[0], ast.ListComp):
                 self.violations.append({
                    'id': 'unnecessary_generator_list',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': f'Using list comprehension with {node.func.id}(). Use generator expression to save memory.',
                    'pattern_match': 'generator_list_comp'
                })

        # Rule: Eager Logging Formatting
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
            is_logger = False
            # Check for logger.info or logging.info
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ['logger', 'logging']:
                is_logger = True
            # Check for self.logger.info or similar attributes ending in logger
            elif isinstance(node.func.value, ast.Attribute) and (node.func.value.attr == 'logger' or node.func.value.attr.endswith('_logger')):
                is_logger = True

            if is_logger and node.args and isinstance(node.args[0], ast.JoinedStr):
                self.violations.append({
                    'id': 'eager_logging_formatting',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': 'Using f-string in logging. Use lazy formatting (e.g. logger.info("%s", val)) to avoid unnecessary string interpolation.',
                    'pattern_match': 'eager_logging'
                })

        # Rule: Unnecessary Comprehension (list([...]) or set({...}))
        if isinstance(node.func, ast.Name) and node.func.id in ['list', 'set', 'dict']:
            if node.args and isinstance(node.args[0], (ast.ListComp, ast.SetComp, ast.DictComp)):
                 self.violations.append({
                    'id': 'unnecessary_comprehension',
                    'line': node.lineno,
                    'severity': 'major',
                    'message': f'Unnecessary comprehension inside {node.func.id}(). Remove brackets for generator expression or use constructor directly.',
                    'pattern_match': 'unnecessary_comp'
                })

        # Rule: Numpy Sum vs Python Sum
        if isinstance(node.func, ast.Name) and node.func.id == 'sum':
            # Heuristic: Check if arg looks like a numpy array (e.g., np_arr, arr) or function call like np.array()
            if node.args:
                arg = node.args[0]
                is_numpy = False
                if isinstance(arg, ast.Name):
                    if arg.id.startswith('np_') or 'array' in arg.id:
                        is_numpy = True
                    elif self.var_types.get(arg.id) == 'numpy':
                        is_numpy = True
                elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
                    # check for np.something
                    if isinstance(arg.func.value, ast.Name) and arg.func.value.id in ['np', 'numpy']:
                        is_numpy = True

                if is_numpy:
                     self.violations.append({
                        'id': 'numpy_sum_vs_python_sum',
                        'line': node.lineno,
                        'severity': 'minor',
                        'message': 'Using python sum() on numpy array. Use np.sum() for better performance.',
                        'pattern_match': 'numpy_sum'
                    })

        # Rule: Subprocess Run Without Timeout
        if func_name == 'subprocess.run' or (isinstance(node.func, ast.Attribute) and node.func.attr == 'run' and
                                             isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess'):
            has_timeout = False
            for keyword in node.keywords:
                if keyword.arg == 'timeout':
                    has_timeout = True
                    break

            if not has_timeout:
                 self.violations.append({
                    'id': 'subprocess_run_without_timeout',
                    'line': node.lineno,
                    'severity': 'major',
                    'message': 'subprocess.run() called without timeout. Can cause hangs.',
                    'pattern_match': 'subprocess_timeout'
                })

        # Rule: Requests Without Timeout
        if func_name and (func_name.startswith('requests.') or func_name == 'requests'):
             # Check if method is one that makes a request (get, post, put, delete, etc)
             # or generic request()
             method = func_name.split('.')[-1] if '.' in func_name else None
             if method in ['get', 'post', 'put', 'delete', 'head', 'options', 'patch', 'request']:
                 has_timeout = False
                 for keyword in node.keywords:
                     if keyword.arg == 'timeout':
                         has_timeout = True
                         break

                 if not has_timeout:
                     self.violations.append({
                        'id': 'requests_without_timeout',
                        'line': node.lineno,
                        'severity': 'major',
                        'message': 'requests call without timeout. Default is infinite, which can hang indefinitely.',
                        'pattern_match': 'requests_timeout'
                    })

        # Rule: SQL Injection (Basic)
        # Detect cursor.execute(f"...") or cursor.execute("..." % ...)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
             # Heuristic: Check if arg is an f-string or % formatting
             if node.args:
                 arg = node.args[0]
                 is_sql_injection = False
                 if isinstance(arg, ast.JoinedStr): # f-string
                     is_sql_injection = True
                 elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod): # % formatting
                     is_sql_injection = True
                 elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'format': # .format()
                     is_sql_injection = True

                 if is_sql_injection:
                     self.violations.append({
                        'id': 'sql_injection_risk',
                        'line': node.lineno,
                        'severity': 'critical',
                        'message': 'Possible SQL injection detected. Use parameterized queries instead of string formatting.',
                        'pattern_match': 'sql_injection'
                    })

        self.generic_visit(node)
    
    def visit_Global(self, node: ast.Global) -> None:
        """Detect global variable usage."""
        self.violations.append({
            'id': 'global_variable_mutation',
            'line': node.lineno,
            'severity': 'minor',
            'message': 'Global variable usage detected. Can hinder optimization.',
            'pattern_match': 'global_keyword'
        })
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect try-except blocks inside loops."""
        if self.in_loop:
             self.violations.append({
                'id': 'exceptions_in_loop',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Try/Except block inside loop. Exception handling is expensive.',
                'pattern_match': 'try_in_loop'
            })
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Detect bare except clauses."""
        if node.type is None:
            self.violations.append({
                'id': 'bare_except',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Bare except clause detected. Catch specific exceptions.',
                'pattern_match': 'bare_except'
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Detect empty classes."""
        self._check_empty_block(node, 'class')
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detect high complexity functions and deep recursion."""
        self._check_function_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Detect blocking I/O in async functions."""
        prev_in_async = self.in_async
        self.in_async = True

        self._check_function_def(node)

        self.in_async = prev_in_async

    def _check_function_def(self, node: [ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
        """Common logic for FunctionDef and AsyncFunctionDef."""
        self._check_empty_block(node, 'function')
        prev_function = self.current_function
        self.current_function = node.name

        # Scope handling for variable types
        prev_var_types = self.var_types.copy()
        self.var_types = {}
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(node)
        
        if complexity > 10:
            self.violations.append({
                'id': 'high_cyclomatic_complexity',
                'line': node.lineno,
                'severity': 'medium',
                'message': f'Function has high cyclomatic complexity ({complexity}). More code paths = more CPU execution.',
                'pattern_match': 'complex_function'
            })
        
        # Rule: Deep Recursion
        if self._is_recursive(node):
             self.violations.append({
                'id': 'deep_recursion',
                'line': node.lineno,
                'severity': 'major',
                'message': f'Recursive function "{node.name}" detected. Deep recursion consumes significant stack memory and CPU.',
                'pattern_match': 'recursive_function'
            })

        # Rule: Mutable Default Arguments
        defaults = node.args.defaults + node.args.kw_defaults
        if defaults:
            for default in defaults:
                if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                     self.violations.append({
                        'id': 'mutable_default_argument',
                        'line': node.lineno,
                        'severity': 'major',
                        'message': 'Mutable default argument detected. Use None and initialize inside function.',
                        'pattern_match': 'mutable_default'
                    })

        self.generic_visit(node)
        self.var_types = prev_var_types # Restore scope
        self.current_function = prev_function

    def _is_recursive(self, node: [ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """Check if function calls itself."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == node.name:
                    return True
        return False
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track imports for unused detection."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments."""
        # Check for string accumulation in loop: s = s + ...
        if self.in_loop and isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Check if variable is a string (and accumulating)
                    if self.var_types.get(var_name) == 'str':
                         # Check if variable is on RHS (recursively)
                         is_rhs = False
                         for child in ast.walk(node.value):
                             if isinstance(child, ast.Name) and child.id == var_name:
                                 is_rhs = True
                                 break

                         if is_rhs:
                             self.violations.append({
                                'id': 'string_concatenation_in_loop',
                                'line': node.lineno,
                                'severity': 'medium',
                                'message': 'String concatenation in loop creates O(n²) memory allocations. Use list.append() and "".join().',
                                'pattern_match': 'string_concat_loop'
                            })
                             break

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.unused_variables[target.id] = node.lineno
                # Try to infer type
                if isinstance(node.value, ast.List) or (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'list'):
                    self.var_types[target.id] = 'list'
                elif isinstance(node.value, (ast.Set, ast.Dict)) or (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id in ['set', 'dict']):
                    self.var_types[target.id] = 'efficient'
                elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    self.var_types[target.id] = 'str'
                elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                     # Check np.array()
                     if isinstance(node.value.func.value, ast.Name) and node.value.func.value.id in ['np', 'numpy'] and node.value.func.attr == 'array':
                         self.var_types[target.id] = 'numpy'
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Track variable usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
        self.generic_visit(node)
    
    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect magic numbers (Python 3.8+)."""
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if node.value > 100 and node.value not in [1000, 1024, 60, 3600]: # Exempt common constants
                self.violations.append({
                    'id': 'magic_numbers',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': f'Magic number "{node.value}" usage. Use named constants.',
                    'pattern_match': 'magic_number'
                })
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Detect context managers (proper cleanup)."""
        # Track items in with statements to identify manual open() calls elsewhere
        self.generic_visit(node)


    
    def _is_in_context_manager(self, call_node) -> bool:
        """Check if call is within a with statement."""
        # Simplified check - would need to track parent nodes properly
        return False
    
    def _calculate_cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
        return complexity
    
    def _detect_unused_variables(self) -> None:
        """Detect unused variables."""
        for var_name, line_num in self.unused_variables.items():
            if var_name not in self.used_variables and not var_name.startswith('_'):
                self.violations.append({
                    'id': 'unused_variables',
                    'line': line_num,
                    'severity': 'medium',
                    'message': f'Unused variable "{var_name}". Remove to free memory.',
                    'pattern_match': 'unused_var'
                })
    
    def _detect_unused_imports(self) -> None:
        """Detect unused imports."""
        for import_name, line_num in self.imports.items():
            if import_name not in self.used_variables:
                self.violations.append({
                    'id': 'unused_imports',
                    'line': line_num,
                    'severity': 'low',
                    'message': f'Unused import "{import_name}". Module load adds startup time and memory.',
                    'pattern_match': 'unused_import'
                })

    def _check_empty_block(self, node, block_type: str) -> None:
        """Check if a block is empty (pass or ...)."""
        if not hasattr(node, 'body'):
            return
            
        is_empty = False
        if not node.body:
             is_empty = True
        elif len(node.body) == 1:
             stmt = node.body[0]
             if isinstance(stmt, ast.Pass):
                 is_empty = True
             elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                 is_empty = True
        
        if is_empty:
             self.violations.append({
                'id': 'empty_block',
                'line': node.lineno,
                'severity': 'minor',
                'message': f'Empty {block_type} detected. Remove or implement.',
                'pattern_match': 'empty_block'
            })
