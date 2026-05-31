import click
import json
import os
from pathlib import Path
from src.core.sbom.generator import SBOMGenerator
from src.core.export.esg_exporter import ESGExporter
from src.core.scanner.main import Scanner

@click.command('sbom')
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['cyclonedx', 'spdx']), default='cyclonedx', help='SBOM format')
@click.option('--output', help='Output file path')
@click.option('--esg-report', is_flag=True, help='Generate ESG compliance report')
def sbom(path, format, output, esg_report):
    """Generate SBOM for a repository"""
    click.echo(f"Generating {format} SBOM for {path}...")

    path_obj = Path(path)
    components = []

    if (path_obj / 'requirements.txt').exists():
        components.append({
            "name": "sample-python-pkg",
            "version": "1.0.0",
            "purl": "pkg:pip/sample-python-pkg@1.0.0",
            "licenses": [{"license": {"id": "MIT"}}]
        })

    generator = SBOMGenerator(project_name=path_obj.name)

    if format == 'cyclonedx':
        result = generator.generate_cyclonedx(components)
    else:
        result = generator.generate_spdx(components)

    output_path = output or f"output/sbom-{path_obj.name}.json"
    os_output_path = Path(output_path)
    os_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(os_output_path, 'w') as f:
        json.dump(result, f, indent=2)

    click.echo(f"[OK] SBOM generated at {os_output_path}")

    if esg_report:
        click.echo("Generating ESG compliance report...")
        scanner = Scanner()
        results = scanner.scan(path)
        exporter = ESGExporter()
        pdf_path = exporter.export(results, project_name=path_obj.name)
        click.echo(f"[OK] ESG Report generated at {pdf_path}")
