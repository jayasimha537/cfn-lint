"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import hashlib
import json
import warnings

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class ListDuplicates(CloudFormationLintRule):
    """Check if duplicates exist in a List"""

    id = "E3037"
    shortdesc = "Check if a list has duplicate values"
    description = (
        "Certain lists don't support duplicate items. "
        "Check when duplicates are provided but not supported."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue"
    tags = ["resources", "property", "list"]

    def match(self, cfn):
        warnings.warn("This rule needs to be rewritten", RuntimeWarning)
