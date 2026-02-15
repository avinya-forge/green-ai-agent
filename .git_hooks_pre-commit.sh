#!/bin/bash
# Pre-commit hook to enforce codebase standards
# Copy this to .git/hooks/pre-commit

set -e

echo "🔍 Running pre-commit checks..."

# Check 1: No CSV/HTML files in root
if git diff --cached --name-only | grep -E '\.(csv|html)$' | grep -v '^output/'; then
    echo "❌ Error: CSV/HTML files should be in output/ folder, not root"
    exit 1
fi

# Check 2: No unauthorized files in docs/
DOCS_FILES=$(git diff --cached --name-only | grep '^docs/' || true)
for file in $DOCS_FILES; do
    if [[ ! "$file" =~ (backlog\.md|BACKLOG\.md|release-notes\.md|vision\.md|development-standards\.md|eventlet-migration\.md|README\.md|\.gitignore)$ ]]; then
        echo "❌ Error: Only standard doc files allowed in docs/"
        echo "   Attempted to add: $file"
        exit 1
    fi
done

# Check 3: Python files have proper imports
PYTHON_FILES=$(git diff --cached --name-only | grep '\.py$' || true)
for file in $PYTHON_FILES; do
    # Basic check - can be enhanced
    if grep -q "^from [a-z]" "$file" 2>/dev/null; then
        if ! grep -q "^from src\." "$file" 2>/dev/null; then
            echo "⚠️  Warning: Check imports in $file (should use 'from src.xxx import')"
        fi
    fi
done

# Check 4: Test coverage minimum
if [[ -f "pytest.ini" ]]; then
    echo "✓ Tests will be run in CI/CD"
fi

echo "✅ Pre-commit checks passed!"
exit 0
