import os
import re

replacements = [
    (r"from agentic_workflow\.domain\.value_objects\.repo_map import", "from agentic_workflow.domain.value_objects import"),
    (r"from agentic_workflow\.domain\.entities\.traceable_id import", "from agentic_workflow.domain.value_objects import"), # TraceLink is in value_objects
    (r"from agentic_workflow\.domain\.entities\.traceable_id import TraceableID", "from agentic_workflow.domain.entities.traceable_id import TraceableID"), # Exception
]

def update_file(filepath):
    if "update_imports.py" in filepath:
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, repl in replacements:
        new_content = re.sub(pattern, repl, new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

for root, dirs, files in os.walk("src"):
    for file in files:
        if file.endswith(".py"):
            update_file(os.path.join(root, file))

for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            update_file(os.path.join(root, file))
