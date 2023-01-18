"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from typing import List
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from jsonschema import validate, Draft7Validator

LOGGER = logging.getLogger("cfnlint")


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = "Validates that GetAtt parameters are to valid resources and properties of those resources"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]

    def _context_picker(self, contexts, path: List[str]) -> RuleMatch:
        match: None = None
        enum_0_message: str = ""
        enum_0_list: set = set()

        for context in contexts:
            if context.validator == "enum":
                if len(context.path) > 0:
                    if context.path[0] == 0:
                        enum_0_message = f"'{context.instance}' is not one of "
                        enum_0_list.update(context.validator_value)
                        match = None
                    elif context.path[0] == 1 and not enum_0_list:
                        match = RuleMatch(path=path, message=context.message)
                else:
                    # deque length is 0.  Should be a string but could be an object or another type
                    if isinstance(context.instance, str):
                        match = RuleMatch(path=path, message=context.message)
                    else:
                        match = RuleMatch(path=path, message=f"Fn::GetAtt should be a list or a string")

        if enum_0_list:
            match = RuleMatch(path=path, message=f"{enum_0_message} {list(enum_0_list)}")

        return match or RuleMatch(path=path, message=f"Fn::GetAtt should be a list or a string")
            

    def match(self, cfn):
        matches = []
        getatts = cfn.search_deep_keys("Fn::GetAtt")
        valid_getatts = cfn.get_valid_getatts()

        schema = valid_getatts.json_schema("us-east-1")

        for getatt in getatts:
            v = Draft7Validator(schema=schema)
            for err in v.iter_errors(getatt[-1]):
                matches.append(self._context_picker(err.context, getatt[0:-1]))  

        return matches
