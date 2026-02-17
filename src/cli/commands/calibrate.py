import click
import os
from src.core.calibration import CalibrationAgent

@click.command()
def calibrate():
    """Run system benchmarks to calibrate carbon models"""
    click.echo("Running system calibration benchmarks...")
    agent = CalibrationAgent()
    profile = agent.run_calibration()

    click.echo(f"\n[OK] Calibration complete!")
    click.echo(f"  Platform: {profile['platform']}")
    click.echo(f"  CPU Count: {profile['cpu_count']}")
    click.echo(f"  System Multiplier: {profile['coefficients']['cpu_multiplier']}x")
    click.echo(f"  Efficiency Tier: {profile['coefficients']['efficiency_tier']}")
    click.echo(f"  Profile saved to: {os.path.abspath(agent.data_path)}")
