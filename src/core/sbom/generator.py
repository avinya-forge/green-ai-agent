import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class SBOMGenerator:
    """Generates SBOMs in CycloneDX and SPDX formats"""

    def __init__(self, project_name: str, version: str = "1.0.0"):
        self.project_name = project_name
        self.version = version
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.urn_uuid = f"urn:uuid:{uuid.uuid4()}"

    def generate_cyclonedx(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate CycloneDX 1.5 JSON SBOM"""
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": self.urn_uuid,
            "version": 1,
            "metadata": {
                "timestamp": self.timestamp,
                "component": {
                    "name": self.project_name,
                    "version": self.version,
                    "type": "application"
                }
            },
            "components": []
        }

        for comp in components:
            sbom["components"].append({
                "name": comp.get("name"),
                "version": comp.get("version"),
                "type": "library",
                "purl": comp.get("purl"),
                "licenses": comp.get("licenses", []),
                "externalReferences": comp.get("externalReferences", [])
            })

        return sbom

    def generate_spdx(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SPDX 2.3 JSON SBOM"""
        sbom = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": self.project_name,
            "documentNamespace": f"https://green-ai.org/spdx/{self.project_name}-{uuid.uuid4()}",
            "creationInfo": {
                "creators": ["Tool: Green-AI-Agent"],
                "created": self.timestamp
            },
            "packages": []
        }

        for i, comp in enumerate(components):
            sbom["packages"].append({
                "name": comp.get("name"),
                "SPDXID": f"SPDXRef-Pkg-{i}",
                "versionInfo": comp.get("version"),
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": comp.get("purl")
                    }
                ] if comp.get("purl") else []
            })

        return sbom
