"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.AllowedValue import (
    AllowedValue,  # pylint: disable=E0401
)


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def test_allowed_value(self):
        """Test Positive"""
        rule = AllowedValue()
        validator = Draft7Validator({"type": "string", "enum": ["a", "b"]})
        self.assertEqual(len(list(rule.enum(validator, ["a", "b"], "a", {}))), 0)
        self.assertEqual(len(list(rule.enum(validator, ["a", "b"], "c", {}))), 1)
        self.assertEqual(len(list(rule.enum(validator, [0, 2], 0, {}))), 0)
        self.assertEqual(len(list(rule.enum(validator, [0, 2], 1, {}))), 1)
