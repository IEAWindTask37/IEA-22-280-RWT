import os

import requests
from jsonschema import ValidationError, validate
from ruamel.yaml import YAML

# pull schema
wio_tur_schema = requests.get(
    "https://raw.githubusercontent.com/IEAWindTask37/windIO/master/windIO/turbine/IEAontology_schema.yaml"
).text

yaml = YAML(typ="safe")
# Load dicts
# schema
schema_dict = yaml.load(wio_tur_schema)

# IEA 22 with monopile
with open("IEA-22-280-RWT.yaml") as file:
    wio_dict = yaml.load(file)

# IEA 22 with floater
with open("IEA-22-280-RWT_Floater.yaml") as file:
    wio_floater_dict = yaml.load(file)


# Set additionalProperties=False for all parts of the schema with properties
def set_additionalPropterties_false(jsonschema_dict):
    if "properties" in jsonschema_dict:
        jsonschema_dict["additionalProperties"] = False
    for name, val in jsonschema_dict.items():
        if isinstance(val, dict):
            jsonschema_dict[name] = set_additionalPropterties_false(val)
        if isinstance(val, list):
            for iel, el in enumerate(val):
                if isinstance(el, dict):
                    jsonschema_dict[name][iel] = set_additionalPropterties_false(el)
    return jsonschema_dict


schema_dict = set_additionalPropterties_false(schema_dict)

# Bugfix for monopile schema
schema_dict["properties"]["components"]["properties"]["monopile"]["properties"][
    "outer_shape_bem"
] = schema_dict["properties"]["components"]["properties"]["monopile"]["properties"].pop(
    "outer_shape"
)

# Bugfix for monopile drag-coefficient
wio_dict["components"]["monopile"]["outer_shape_bem"]["drag_coefficient"] = dict(
    grid=[0, 1], values=[0.5, 0.5]
)

# Bugfix for mooring node
for node in wio_floater_dict["components"]["mooring"]["nodes"]:
    node["location"] = [0, 0, 0]


# Remove properties that are not declared by the schema
def remove_prop(dict_in, remove_props):
    for name, val in remove_props.items():
        if isinstance(val, dict):
            dict_in[name] = remove_prop(dict_in[name], val)
        elif isinstance(name, int):
            dict_in[name] = remove_prop(dict_in[name], val)
        elif val is None:
            dict_in.pop(name, None)
    return dict_in


def add_prop(dict_in, path_list, val):
    if len(path_list) == 1:
        dict_in[path_list[0]] = val
        return dict_in
    name = path_list[0]
    dict_in[name] = add_prop(dict_in.get(name, dict()), path_list[1:], val)
    return dict_in


def get_undefined_properties(wio_dict, schema, n_max=100):
    undefined_props = dict()
    fails = True
    n = 0
    while fails and n < n_max:
        try:
            validate(wio_dict, schema)
            fails = False
        except ValidationError as err:
            if err.validator == "additionalProperties":
                if "was unexpected" in err.message:
                    names = {
                        err.message.split("(")[-1].split(" was")[0].strip("' "): None
                    }
                else:
                    names = {
                        name.strip("' "): None
                        for name in err.message.split("(")[-1]
                        .split("were")[0]
                        .split(",")
                    }
                undefined_props = add_prop(undefined_props, list(err.path), names)
                wio_dict = remove_prop(wio_dict, undefined_props)
            else:
                raise ValueError(err.message)
        n += 1

    return undefined_props


wio_undefinined_fname = "IEA-22-280-RWT_undefined.yaml"
if os.path.isfile(wio_undefinined_fname):
    with open(wio_undefinined_fname, "r") as file:
        wio_undefined_properties = yaml.load(file)
    wio_dict = remove_prop(wio_dict, wio_undefined_properties)
else:
    wio_undefined_properties = get_undefined_properties(wio_dict, schema_dict)
    with open(wio_undefinined_fname, "w") as file:
        yaml.dump(wio_undefined_properties, file)

wio_floater_undefinined_fname = "IEA-22-280-RWT_Floater_undefined.yaml"
if os.path.isfile(wio_floater_undefinined_fname):
    with open(wio_floater_undefinined_fname, "r") as file:
        wio_floater_undefined_properties = yaml.load(file)
    wio_floater_dict = remove_prop(wio_floater_dict, wio_floater_undefined_properties)
else:
    wio_floater_undefined_properties = get_undefined_properties(
        wio_floater_dict, schema_dict
    )
    with open(wio_floater_undefinined_fname, "w") as file:
        yaml.dump(wio_floater_undefined_properties, file)

# Validate is windIO
validate(wio_dict, schema_dict)
validate(wio_floater_dict, schema_dict)
