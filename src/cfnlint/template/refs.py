from functools import lru_cache
from typing import Dict, Sequence, Union, List

from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class RefsSchemas:
    SINGULAR_SCHEMA: Dict
    LIST_SCHEMA: Dict

class Refs:

    _refs: Dict[str, Dict[str, Dict]]

    def __init__(self, regions: List[str]) -> None:
        for region in regions:
            self._refs[region] = {}

    def _convert_parameter_type_to_schema(self, parameter_type: str) -> Dict:
        if "List<Number>" in parameter_type:
            return {
                "type": "array",
                "items": {
                    "type": "number",
                },
            }

        if "List<" in parameter_type or "CommaDelimitedList" in parameter_type:
            return {
                "type": "array",
                "items": {
                    "type": "string",
                },
            }
        if parameter_type == "Number":
            return {
                "type": "number",
            }

        return {
            "type": "string",
        }

    def add_parameter(self, parameter_name: str, parameter_type: str) -> None:
        for region in self._refs.keys():
            if parameter_name not in self._refs[region]:
                self._refs[region][parameter_name] = self._convert_parameter_type_to_schema(parameter_type=parameter_type)

    def add_resource(self, resource_name: str, resource_type: str) -> None:
        for region in self._refs.keys():
            if resource_name not in self._refs[region]:
                self._refs[region][resource_name] = {}
                self._refs[region][resource_name] = PROVIDER_SCHEMA_MANAGER.get_type_ref(
                    resource_type=resource_type, region=region
                )

    def json_schema(self, region: str, is_array: bool=False) -> Dict:
        r"""
            Provide the json schema for validating a Ref
        """
        schema = {
            "type": "string",
            "enum": []
        }

        for ref_name in self._refs[region]:
            schema["enum"].append(ref_name)

        return schema

    @lru_cache
    def match(self, ref: str, region: str) -> Dict:
        if isinstance(ref, str):
            try:
                result = self._refs[region].get(ref)
                if result is None:
                    raise ValueError("Ref doesn't exist")
                return result
            except ValueError as e:
                raise e
        else:
            raise (TypeError("Invalid Ref structure"))
