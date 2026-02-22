import json
from pathlib import Path
from src.core.config_models import GreenAIConfig

def generate_schema():
    """Generate JSON schema for GreenAIConfig."""
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    schema_path = output_dir / 'schema.json'

    with open(schema_path, 'w') as f:
        json.dump(GreenAIConfig.model_json_schema(), f, indent=2)

    print(f"Schema generated at: {schema_path}")

if __name__ == "__main__":
    generate_schema()
