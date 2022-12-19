"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class StringSize(CloudFormationLintRule):
    """Check if a String has a length within the limit"""

    id = "E3033"
    shortdesc = "Check if a string has between min and max number of values specified"
    description = "Check strings for its length between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "string", "size"]

