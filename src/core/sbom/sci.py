from typing import Dict, Any, Optional

class SCICalculator:
    """
    GSF Software Carbon Intensity (SCI) calculator.
    Formula: SCI = (E * I + M) / R
    E: Energy (kWh)
    I: Carbon Intensity (gCO2eq/kWh)
    M: Embodied Emissions (gCO2eq)
    R: Functional Unit (e.g., per user, per request, per API call)
    """

    def __init__(self, carbon_intensity: float = 475.0, embodied_emissions: float = 0.0):
        self.I = carbon_intensity  # Default global avg gCO2/kWh
        self.M = embodied_emissions

    def calculate(self, energy_kwh: float, functional_unit_count: float = 1.0) -> float:
        """Calculate SCI score"""
        if functional_unit_count <= 0:
            return 0.0

        sci = (energy_kwh * self.I + self.M) / functional_unit_count
        return sci

    def get_sci_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SCI report from scan results"""
        # Estimate energy from emissions (emissions = energy * intensity)
        # emissions is in kg CO2. I is in g CO2/kWh.
        # kg_emissions * 1000 / intensity = kWh
        total_kg_co2 = results.get('codebase_emissions', 0.0)
        estimated_kwh = (total_kg_co2 * 1000) / self.I if self.I > 0 else 0.0

        # Default R to total files scanned if not provided
        R = results.get('metadata', {}).get('total_files', 1.0)

        sci_score = self.calculate(estimated_kwh, R)

        return {
            "sci_score": sci_score,
            "energy_kwh": estimated_kwh,
            "carbon_intensity": self.I,
            "embodied_emissions": self.M,
            "functional_unit": "per file scanned",
            "functional_unit_count": R,
            "unit": "gCO2eq / per file scanned"
        }
