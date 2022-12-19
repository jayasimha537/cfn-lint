"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class AllowedPattern(CloudFormationLintRule):
    """Check if properties have a valid value"""

    id = "E3031"
    shortdesc = "Check if property values adhere to a specific pattern"
    description = "Check if properties have a valid value in case of a pattern (Regular Expression)"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "allowed pattern", "regex"]

