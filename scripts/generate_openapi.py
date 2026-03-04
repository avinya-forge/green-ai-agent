import yaml
import json
import os
from src.ui.app_fastapi import app

def generate_openapi():
    # Generate OpenAPI schema
    openapi_schema = app.openapi()

    # Create docs/api directory if it doesn't exist
    os.makedirs("docs/api", exist_ok=True)

    # Save to yaml
    with open("docs/api/swagger.yaml", "w") as f:
        yaml.dump(openapi_schema, f, default_flow_style=False)

    print("Generated docs/api/swagger.yaml")

    # Generate Mock Data
    mock_data = {}

    # Extract components/schemas if they exist
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
        for schema_name, schema_props in schemas.items():
            mock_data[schema_name] = generate_mock_from_schema(schema_props)

    # Save mock data
    with open("docs/api/mock_data.json", "w") as f:
        json.dump(mock_data, f, indent=2)

    print("Generated docs/api/mock_data.json")

def generate_mock_from_schema(schema):
    mock = {}
    properties = schema.get("properties", {})
    for prop_name, prop_details in properties.items():
        prop_type = prop_details.get("type", "string")
        if prop_type == "string":
            mock[prop_name] = "string"
        elif prop_type == "integer":
            mock[prop_name] = 0
        elif prop_type == "number":
            mock[prop_name] = 0.0
        elif prop_type == "boolean":
            mock[prop_name] = True
        elif prop_type == "array":
            items = prop_details.get("items", {})
            mock[prop_name] = [generate_mock_from_schema(items) if "properties" in items else "item"]
        elif prop_type == "object":
            mock[prop_name] = generate_mock_from_schema(prop_details)
        elif "$ref" in prop_details:
            mock[prop_name] = "ref_" + prop_details["$ref"].split("/")[-1]
        else:
            mock[prop_name] = "unknown"
    return mock

if __name__ == "__main__":
    generate_openapi()
