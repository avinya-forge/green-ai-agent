import click
import json
from pathlib import Path
from src.core.scanner.main import Scanner
from src.core.sbom.generator import SBOMGenerator
from src.core.export.esg_exporter import ESGExporter


@click.command('sbom')
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', 'sbom_format', type=click.Choice(['cyclonedx', 'spdx']), default='cyclonedx', help='SBOM format')
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--esg-report', is_flag=True, help='Generate ESG compliance report PDF')
def sbom(path, sbom_format, output, esg_report):
    """Generate Software Bill of Materials (SBOM) for compliance"""
    if esg_report:
        click.echo(f"Generating ESG report for {path}...")
    else:
        click.echo(f"Generating {sbom_format} SBOM for {path}...")

    scanner = Scanner()
    results = scanner.scan(path)

    if esg_report:
        exporter = ESGExporter(output_path=output)
        report_path = exporter.export(results, project_name=str(Path(path).name))
        click.echo(f"[OK] ESG Report generated at {report_path}")
        return

    # Simplified: in real life would parse dependencies
    components = []
    # Using codebase emissions keys as a proxy for scanned files
    for file_path in results.get('per_file_emissions', {}).keys():
        components.append({
            "name": Path(file_path).name,
            "version": "0.0.1",
            "purl": f"pkg:generic/{Path(file_path).name}@0.0.1"
        })

    generator = SBOMGenerator(project_name=str(Path(path).name))
    if sbom_format == 'cyclonedx':
        sbom_data = generator.generate_cyclonedx(components)
    else:
        sbom_data = generator.generate_spdx(components)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(sbom_data, f, indent=2)
        click.echo(f"[OK] SBOM exported to {output}")
    else:
        click.echo(json.dumps(sbom_data, indent=2))
