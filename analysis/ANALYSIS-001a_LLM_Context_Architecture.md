# ANALYSIS-001a: LLM Context Architecture Feasibility

## Objective
Define an architecture for passing AST (Abstract Syntax Tree) context to LLMs without exceeding token limits, ensuring high-quality and context-aware code auto-fixes.

## Current Limitations
- Raw source code files can easily exceed the context windows of cheaper models (e.g., standard GPT-3.5 or smaller Ollama models).
- Passing the entire file includes irrelevant context, which wastes tokens and can distract the LLM from the actual violation.
- ASTs represented as raw JSON or S-expressions are heavily nested and consume a massive amount of tokens compared to standard text.

## Proposed Architecture: Context Windowing & Pruning

### 1. Snippet Extraction via AST
Instead of passing the entire file or the entire AST tree, we use the `tree-sitter` parsed AST to extract only the relevant snippet.
- **Node Identification:** Locate the specific AST node triggering the rule violation.
- **Scope Expansion:** Traverse up the tree to find the nearest enclosing scope (e.g., function definition or class definition).
- **Pruning:** Extract the source code of *only* this enclosing scope.

### 2. Prompt Structuring
The prompt sent to the LLM should be structured to provide maximum clarity with minimal tokens:

```markdown
You are a Green-AI remediation assistant. Fix the following code to resolve the violation.

Violation: [Rule Name/Message]
Line: [Line Number relative to snippet]

Code Snippet:
[Pruned Code String]

Return ONLY the fixed code snippet.
```

### 3. Token Estimation & Chunking
Before sending the request:
- Use a lightweight token estimator (e.g., `tiktoken` for OpenAI) locally.
- If the extracted scope exceeds the predefined token limit (e.g., 4000 tokens), apply a fallback strategy:
  - **Fallback A:** Extract only `N` lines above and below the specific violation node, rather than the entire function.
  - **Fallback B:** Return an error to the user indicating the code block is too complex for automated remediation (promotes refactoring).

## Feasibility Conclusion
**Highly Feasible.** By leveraging the existing `tree-sitter` integration to intelligently window the source code, we can guarantee that payload sizes remain well within limits, thus keeping API costs low and inference times fast.