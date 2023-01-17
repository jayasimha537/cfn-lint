from functools import lru_cache
from typing import Dict, Sequence, Union, List

from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.helpers import RegexDict


class GetAtts:

    # [region][resource_name][attribute][JsonSchema Dict]
    _getatts: Dict[str, Dict[str, RegexDict]]

    _astrik_string_types = ("AWS::CloudFormation::Stack",)
    _astrik_unknown_types = (
        "Custom::",
        "AWS::Serverless::",
        "AWS::CloudFormation::CustomResource",
    )

    def __init__(self, regions: List[str]) -> None:
        self._regions = regions
        self._getatts = {}
        for region in self._regions:
            self._getatts[region] = {}

    def add(self, resource_name: str, resource_type: str) -> None:
        for region in self._regions:
            if resource_name not in self._getatts[region]:
                self._getatts[region][resource_name] = {}
                if resource_type.startswith(self._astrik_string_types):
                    self._getatts[region][resource_name]["*"] = {"type": "string"}
                elif resource_type.startswith(
                    self._astrik_unknown_types
                ) or resource_type.endswith("::MODULE"):
                    self._getatts[region][resource_name]["*"] = {}
                else:
                    for (
                        attr_name,
                        attr_value,
                    ) in PROVIDER_SCHEMA_MANAGER.get_type_getatts(
                        resource_type=resource_type, region=region
                    ).items():
                        self._getatts[region][resource_name][attr_name] = attr_value

    def json_schema(self, region: str) -> Dict:

        schema = {"oneOf": []}
        strings = {
            "type": "string",
            "enum": [],
        }

        for resource_name, attributes in self._getatts[region].items():
            attr_enum = []
            for attribute in attributes:
                attr_enum.append(attribute)

                strings["enum"].append(f"{resource_name}.{attribute}")
            schema["oneOf"].append(
                {
                    "type": "array",
                    "items": [
                        {"type": "string", "enum": [resource_name]},
                        {"type": "string", "enum": attr_enum},
                    ],
                }
            )

        schema["oneOf"].append(
            {
                "type": "array",
                "items": [
                    {"type": "string", "enum": [resource_name]},
                    {"type": "object", "properties": {"Ref": {"type": "string"}}},
                ],
            }
        )
        schema["oneOf"].append(strings)
        return schema

    @lru_cache
    def match(self, getatt: Union[str, List[str]], region: str) -> Dict:
        if isinstance(getatt, str):
            getatt = getatt.split(".", 1)

        if isinstance(getatt, list):
            if len(getatt) != 2:
                raise (TypeError("Invalid GetAtt size"))

            try:
                result = self._getatts.get([region][getatt[0]].get(getatt[1]))
                if result is None:
                    raise ValueError("Attribute for resource doesn't exist")
                return result
            except ValueError as e:
                raise e

        else:
            raise (TypeError("Invalid GetAtt structure"))
