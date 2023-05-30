import jsonschema
from typing import Union

def generate_schema(json_doc: Union[dict, list],
                    schema_url: str = None,
                    uri: str = None,
                    title: str = None,
                    description: str = None,
                    required_cols: Union[str, list] = None,
                    nullable_cols: Union[str, list] = None,
                    version: str = None) -> dict:
    """
    Generate a JSON schema based on the input JSON document.

    :param json_doc: The JSON document to generate the schema from.
    :param schema_url: The URL of the schema.
    :param uri: The URI of the schema.
    :param title: The title of the schema.
    :param description: The description of the schema.
    :param required_cols: Columns that are required in the JSON document.
    :param nullable_cols: Columns that can have null values.
    :param version: The version of the schema.
    :return: The generated JSON schema.
    """
    if required_cols is None:
        required_cols = list(json_doc.keys()) if isinstance(json_doc, dict) else []

    if nullable_cols is None:
        nullable_cols = []

    if isinstance(json_doc, dict):
        root_json_type = "object"
        schema = {
            "type": root_json_type,
            "properties": {},
            "required": [],
        }
    elif isinstance(json_doc, list):
        root_json_type = "array"
        schema = {
            "type": root_json_type,
            "items": {},
        }
    else:
        raise ValueError("Invalid JSON document. Must be either a dictionary or a list.")

    if schema_url is not None:
        schema["$schema"] = schema_url

    if uri is not None:
        schema["$id"] = uri

    if title is not None:
        schema["title"] = title

    if description is not None:
        schema["description"] = description

    if version is not None:
        schema['version'] = version

    if isinstance(json_doc, dict):
        for key, value in json_doc.items():
            value_type = type(value).__name__
            if value_type == "list":
                if len(value) > 0:
                    if isinstance(value[0], dict):
                        item_schema = generate_schema(
                            value[0], schema_url, uri, title, description,
                            required_cols, nullable_cols, version
                        )
                        schema["properties"][key] = {
                            "type": "array",
                            "items": item_schema
                        }
                        if key in required_cols:
                            schema["required"].append(key)
            elif value_type == "dict":
                item_schema = generate_schema(
                    value, schema_url, uri, title, description,
                    required_cols, nullable_cols, version
                )
                schema["properties"][key] = item_schema
                if key in required_cols:
                    schema["required"].append(key)
            else:
                if value is None or key in nullable_cols:
                    value_type = ["string", "null"]
                elif value_type == "int":
                    value_type = "integer"
                elif value_type == "str":
                    value_type = "string"
                schema["properties"][key] = {"type": value_type}
                if key in required_cols:
                    schema["required"].append(key)
    elif isinstance(json_doc, list):
        if len(json_doc) > 0:
            if isinstance(json_doc[0], dict):
                item_schema = generate_schema(
                    json_doc[0], schema_url, uri, title, description,
                    required_cols, nullable_cols, version
                )
                schema["items"] = item_schema

    return schema



def validate_json(json_doc, schema):
    try:
        jsonschema.validate(json_doc, schema)
        print("Meets Schema Requirements")
    except jsonschema.exceptions.ValidationError as e:
        print(e)
