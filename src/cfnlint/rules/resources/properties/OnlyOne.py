"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from jsonschema.exceptions import ValidationError

class OnlyOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""

    id = "E2523"
    shortdesc = "Check Properties that need only one of a list of properties"
    description = (
        "Making sure CloudFormation properties "
        + "that require only one property from a list. "
        + "One has to be specified."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

