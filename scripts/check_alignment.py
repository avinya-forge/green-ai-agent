import os
import sys

def check_alignment():
    print("Checking alignment between vision.md and architecture.md...")

    with open('docs/vision.md', 'r') as f:
        vision = f.read().lower()

    with open('docs/architecture.md', 'r') as f:
        arch = f.read().lower()

    pillars = ['environmental', 'security', 'governance', 'ai-fix']
    missing = []

    for pillar in pillars:
        if pillar not in arch:
            missing.append(pillar)

    if missing:
        print(f"FAILED: Architecture does not explicitly reference pillars: {', '.join(missing)}")
        return 1

    print("SUCCESS: All vision pillars found in architecture.")
    return 0

if __name__ == "__main__":
    sys.exit(check_alignment())
