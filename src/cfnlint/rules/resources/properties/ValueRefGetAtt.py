"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import warnings
import cfnlint.helpers
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER

class ValueRefGetAtt(CloudFormationLintRule):
    """Check if Resource Properties are correct"""

    id = "E3008"
    shortdesc = "Check values of properties for valid Refs and GetAtts"
    description = "Checks resource properties for Ref and GetAtt values"
    tags = ["resources", "ref", "getatt"]

    def __init__(self):
        super().__init__()
        self.cfn = None

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    def awsType(self, validator, uI, instance, schema):
        aws_type = schema.get("awsType")
        print(aws_type)
    