from jsonschema import exceptions
from typing import Union, List
from cfnlint.rules import CloudFormationLintRule


class ValidationError(exceptions.ValidationError):
    def __init__(self, message, path=(), context=(), extra_args=None, rule:Union[CloudFormationLintRule, None] = None, path_override: Union[List, None]= None):
        super().__init__(message, path=path, context=context)
        self.extra_args = extra_args or {}
        self.rule = rule
        self.path_override = path_override

