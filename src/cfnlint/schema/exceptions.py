from __future__ import annotations
from jsonschema import exceptions
from typing import Union, List, TYPE_CHECKING
if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule

class ResourceNotFoundError(Exception):
    def __init__(self, type: str, region: str):
        super().__init__(f"Resource type '{type}' is not found in '{region}'")

