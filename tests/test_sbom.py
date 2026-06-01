import json
from src.core.sbom.generator import SBOMGenerator
from src.core.sbom.sci import SCICalculator

def test_cyclonedx_generation():
    gen = SBOMGenerator("test-project", "1.0.0")
    components = [
        {"name": "lib1", "version": "1.2.3", "purl": "pkg:pip/lib1@1.2.3"}
    ]
    sbom = gen.generate_cyclonedx(components)
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["metadata"]["component"]["name"] == "test-project"
    assert len(sbom["components"]) == 1
    assert sbom["components"][0]["name"] == "lib1"

def test_spdx_generation():
    gen = SBOMGenerator("test-project", "1.0.0")
    components = [
        {"name": "lib1", "version": "1.2.3", "purl": "pkg:pip/lib1@1.2.3"}
    ]
    sbom = gen.generate_spdx(components)
    assert sbom["spdxVersion"] == "SPDX-2.3"
    assert sbom["name"] == "test-project"
    assert len(sbom["packages"]) == 1

def test_sci_calculation():
    calc = SCICalculator(carbon_intensity=500.0, embodied_emissions=100.0)
    # SCI = (E * I + M) / R
    # (0.1 * 500 + 100) / 2 = (50 + 100) / 2 = 75.0
    score = calc.calculate(0.1, 2.0)
    assert score == 75.0

def test_sci_report():
    calc = SCICalculator(carbon_intensity=500.0)
    results = {
        'codebase_emissions': 0.0005, # kg CO2 = 0.5g CO2
        'metadata': {'total_files': 5}
    }
    # energy = (0.0005 * 1000) / 500 = 0.001 kWh
    # score = (0.001 * 500 + 0) / 5 = 0.1 gCO2 / file
    report = calc.get_sci_report(results)
    assert report['sci_score'] == 0.1
