from typing import Dict, Any, List


class SBOMGenerator:
    """Generates SBOMs in CycloneDX and SPDX formats."""

    def __init__(self, project_name: str = "unknown", version: str = "1.0.0"):
        self.project_name = project_name
        self.version = version

    def generate_cyclonedx(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CycloneDX 1.5 JSON SBOM."""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "metadata": {
                "component": {
                    "name": self.project_name,
                    "version": self.version,
                    "type": "application"
                }
            },
            "components": components
        }

    def generate_spdx(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SPDX 2.3 JSON SBOM."""
        packages = []
        for comp in components:
            packages.append({
                "name": comp.get("name"),
                "SPDXID": f"SPDXRef-{comp.get('name')}",
                "versionInfo": comp.get("version"),
                "externalRefs": [{"referenceCategory": "PACKAGE-MANAGER", "referenceLocator": comp.get("purl"), "referenceType": "purl"}]
            })

        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": self.project_name,
            "documentNamespace": "https://green-ai.io/sbom",
            "creationInfo": {
                "creators": ["Tool: Green-AI Agent"],
                "created": "2024-01-01T00:00:00Z"
            },
            "packages": packages
        }
