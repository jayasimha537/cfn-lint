from __future__ import annotations
from jsonschema import exceptions
from typing import Union, List, TYPE_CHECKING
if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule


class ValidationError(exceptions.ValidationError):
    def __init__(self, message, path=(), context=(), extra_args=None, rule:Union[CloudFormationLintRule, None] = None, path_override: Union[List, None]= None):
        super().__init__(message, path=path, context=context)
        self.extra_args = extra_args or {}
        self.rule = rule
        self.path_override = path_override


class UndefinedTypeCheck(Exception):
    """
    A type checker was asked to check a type it did not have registered.
    """

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return f"Type {self.type!r} is unknown to this type checker"
