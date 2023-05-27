import jsonschema

def generate_schema(json_doc: dict, schema_url:str=None, required_cols:str or list=None, nullable_cols:str or list=None) -> dict:
    if required_cols is None:
        required_cols = list(json_doc.keys())

    if nullable_cols is None:
        nullable_cols = []

    schema = {
        # "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {},
        "required": []
    }

    for key, value in json_doc.items():
        value_type = type(value).__name__
        if value_type == "list":
            if len(value) > 0:
                if isinstance(value[0], dict):
                    item_schema = generate_schema(value[0], required_cols, nullable_cols)
                    schema["properties"][key] = {
                        "type": "array",
                        "items": item_schema
                    }
                    if key in required_cols:
                        schema["required"].append(key)
        elif value_type == "dict":
            item_schema = generate_schema(value, required_cols, nullable_cols)
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

    return schema




def check_json(json_doc, schema):
    try:
        jsonschema.validate(json_doc, schema)
        print("Valid JSON")
    except jsonschema.exceptions.ValidationError as e:
        print(e)