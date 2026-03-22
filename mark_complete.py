import re

filepath = 'docs/planning/backlog.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Mark TASK AUDIT-004 as done
content = re.sub(
    r"(\*\*TASK AUDIT-004.*?)\[TODO\]",
    r"\1[DONE]",
    content
)
content = re.sub(
    r"(\s+)- \[ \] TASK: UI/UX Error state presentation",
    r"\1- [x] TASK: UI/UX Error state presentation",
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
