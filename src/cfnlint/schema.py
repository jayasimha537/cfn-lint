import sys
from dataclasses import dataclass
from typing import Dict, List, Union
import json
import pkg_resources
from collections import UserDict
from cfnlint.jsonutils import pointer
from copy import deepcopy

# Can't use a dataclass because its hard to parse in json
# with optional fields without addtional help

class Schema():
    _json_schema: Dict

    def __init__(self, schema) -> None:
        self.schema = deepcopy(schema)
        self._json_schema = self._cleanse_schema(schema=schema)

    def _cleanse_schema(self, schema) -> Dict:
        for ro_prop in schema.get("readOnlyProperties", []):
            sub_schema = schema
            for p in ro_prop.split("/")[1:-1]:
                sub_schema = sub_schema.get(p)
                if sub_schema is None:
                    break
            if sub_schema is not None:
                if sub_schema.get(ro_prop.split("/")[-1]) is not None:
                    del sub_schema[ro_prop.split("/")[-1]]

        return schema

    def json_schema(self) -> Dict:
        return self._json_schema

    def get_atts(self) -> Dict[str, dict]:
        attrs = {}
        for ro_attr in self.schema.get('readOnlyProperties', []):
            try:
                attrs[ro_attr.split("/")[-1]] = pointer.resolve(self.schema, ro_attr)
            except KeyError as e:
                pass

        print(attrs)
        return attrs
    
