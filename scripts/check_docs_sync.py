#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def check_docs_sync():
    """
    Check if docs/vision.md and docs/architecture.md are synchronized.
    Checks that every 'Future Extension:' mentioned in vision.md has a corresponding
    section in architecture.md.
    """
    repo_root = Path(__file__).resolve().parent.parent
    vision_path = repo_root / "docs" / "vision.md"
    arch_path = repo_root / "docs" / "architecture.md"

    if not vision_path.exists() or not arch_path.exists():
        print("❌ Error: Missing docs/vision.md or docs/architecture.md")
        sys.exit(1)

    with open(vision_path, "r", encoding="utf-8") as f:
        vision_content = f.read()

    with open(arch_path, "r", encoding="utf-8") as f:
        arch_content = f.read()

    # Extract all future extensions from vision.md
    # Assuming the format is: ## Future Extension: <Extension Name>
    extensions = re.findall(r'## Future Extension:\s*(.*)', vision_content)

    missing_extensions = []
    for ext in extensions:
        if ext.strip() not in arch_content:
            missing_extensions.append(ext.strip())

    if missing_extensions:
        print("❌ Error: docs/architecture.md is out of sync with docs/vision.md.")
        for ext in missing_extensions:
            print(f"   '{ext}' is missing from architecture.md.")
        sys.exit(1)

    print("✅ Documentation is in sync.")
    sys.exit(0)

if __name__ == "__main__":
    check_docs_sync()
