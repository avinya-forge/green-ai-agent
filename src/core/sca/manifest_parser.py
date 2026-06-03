"""
Dependency manifest parser for SCA (Software Composition Analysis).
Parses requirements.txt, package.json, and other manifest files.
"""

import re
import json
from typing import List, Dict


class ManifestParser:
    """
    Parses various dependency manifest formats.
    """

    def parse_requirements_txt(self, content: str) -> List[Dict]:
        """Parse Python requirements.txt."""
        dependencies = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([=><!~]+)([a-zA-Z0-9_\-\.\*]+)', line)
            if match:
                name, op, version = match.groups()
                dependencies.append({
                    'name': name,
                    'version': version,
                    'type': 'python'
                })
            else:
                if re.match(r'^[a-zA-Z0-9_\-\[\]]+$', line):
                    dependencies.append({
                        'name': line,
                        'version': 'unknown',
                        'type': 'python'
                    })
        return dependencies

    def parse_package_json(self, content: str) -> List[Dict]:
        """Parse Node.js package.json."""
        dependencies = []
        try:
            data = json.loads(content)
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})

            for name, version in {**deps, **dev_deps}.items():
                clean_version = re.sub(r'^[~^><=]+', '', version)
                dependencies.append({
                    'name': name,
                    'version': clean_version,
                    'type': 'npm'
                })
        except Exception:
            pass
        return dependencies
