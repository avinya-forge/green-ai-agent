from typing import Dict, Any


class SCICalculator:
    """Calculates Software Carbon Intensity (SCI) based on GSF spec."""

    def __init__(self, carbon_intensity: float = 0.5, embodied_emissions: float = 0.0):
        self.carbon_intensity = carbon_intensity
        self.embodied_emissions = embodied_emissions

    def calculate(self, energy_kwh: float, functional_unit_value: float) -> float:
        """
        Calculate SCI score.
        Formula: SCI = (E * I) + M per R
        """
        if functional_unit_value == 0:
            functional_unit_value = 1

        sci = ((energy_kwh * self.carbon_intensity) + self.embodied_emissions) / functional_unit_value
        return sci

    def get_sci_report(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured SCI report from scan results."""
        codebase_emissions_kg = scan_results.get('codebase_emissions', 0.0)
        # Convert kg CO2 back to estimated kWh using intensity
        # E = Emissions / I
        energy_kwh = (codebase_emissions_kg * 1000) / self.carbon_intensity if self.carbon_intensity > 0 else 0

        total_files = scan_results.get('metadata', {}).get('total_files', 1)
        sci_score = self.calculate(energy_kwh, total_files)

        return {
            'sci_score': sci_score,
            'unit': 'gCO2e/file',
            'energy_kwh': energy_kwh,
            'carbon_intensity': self.carbon_intensity,
            'embodied_carbon': self.embodied_emissions,
            'functional_unit': 'file'
        }
