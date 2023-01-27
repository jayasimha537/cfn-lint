"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

import jsonschema

from cfnlint.rules.resources.properties.ValuePrimitiveType import (  # pylint: disable=E0401
    ValidationError,
    ValuePrimitiveType,
)


class TestResourceValuePrimitiveTypeNonStrict(BaseRuleTestCase):
    """Test Primitive Value Types"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

    def test_file_positive(self):
        """Test Positive"""
        # Test Booleans
        self.assertEqual(
            len(self.rule._value_check("True", ["test"], "Boolean", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("False", ["test"], "Boolean", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Boolean", False, {})), 1
        )
        # Test Strings
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "String", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(2, ["test"], "String", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "String", False, {})), 0
        )
        # Test Integer
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Integer", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Integer", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Integer", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Integer", False, {})), 1
        )
        # Test Double
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Double", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Double", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Double", False, {})), 1
        )
        # Test Long
        self.assertEqual(
            len(
                self.rule._value_check(str(65536 * 65536), ["test"], "Long", False, {})
            ),
            0,
        )
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Long", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1.2", ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(1.2, ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check(65536 * 65536, ["test"], "Long", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Long", False, {})), 1
        )
        self.assertEqual(
            len(self.rule._value_check("test", ["test"], "Long", False, {})), 1
        )
        # Test Unknown type doesn't return error
        self.assertEqual(
            len(self.rule._value_check(1, ["test"], "Unknown", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check("1", ["test"], "Unknown", False, {})), 0
        )
        self.assertEqual(
            len(self.rule._value_check(True, ["test"], "Unknown", False, {})), 0
        )


class TestResourceValuePrimitiveTypeCheckValue(BaseRuleTestCase):
    """Test Check Value for maps"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

    def test_file_check_value_good_function(self):
        results = self.rule.check_value(
            {"key": {"Ref": ["Parameter"]}},
            [],
            primitive_type="String",
            item_type="Map",
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_is_string(self):
        results = self.rule.check_value(
            {"key": 1}, [], primitive_type="Integer", item_type="Map"
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_is_json(self):
        results = self.rule.check_value(
            {"key": {}}, [], primitive_type="Json", item_type="Map"
        )
        self.assertEqual(len(results), 0)

    def test_file_check_value_bad_function(self):
        results = self.rule.check_value(
            {"key": {"Func": ["Parameter"]}},
            [],
            primitive_type="Boolean",
            item_type="Map",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].message,
            "Use a valid function [Fn::Base64, Fn::Cidr, Fn::Contains, "
            "Fn::FindInMap, Fn::GetAtt, Fn::If, Fn::ImportValue, Fn::Join, Fn::Length, "
            "Fn::Select, Fn::Sub, Fn::ToJsonString, Ref] when "
            "providing a value of type [Boolean]",
        )

    def test_file_check_value_bad_object(self):
        results = self.rule.check_value(
            {"key": {"Func": ["Parameter"], "Func2": ["Parameter"]}},
            [],
            primitive_type="String",
            item_type="Map",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].message,
            "Use a valid function [Fn::Base64, Fn::Cidr, Fn::Contains, "
            "Fn::FindInMap, Fn::GetAtt, Fn::If, Fn::ImportValue, Fn::Join, Fn::Length, "
            "Fn::Select, Fn::Sub, Fn::ToJsonString, Ref] when "
            "providing a value of type [String]",
        )

        self.rule.config["strict"] = False

    def test_file_positive(self):
        """Test Positive"""
        # Test Booleans
        self.assertEqual(
            self.rule._schema_check_primitive_type("True", ["boolean"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("False", ["boolean"]), True
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["boolean"]), False)
        # Test Strings
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["string"]), True)
        self.assertEqual(self.rule._schema_check_primitive_type(2, ["string"]), True)
        self.assertEqual(self.rule._schema_check_primitive_type(True, ["string"]), True)
        # Test Integer
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["integer"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["integer"]), False
        )
        # Test Double
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["number"]), True
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["number"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["number"]), False
        )
        # Test multiple types
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["string", "integer"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["boolean", "integer"]),
            False,
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(1.34, ["boolean", "string"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.34", ["boolean", "number"]), True
        )

    def test_positive_strict(self):
        self.rule.config["strict"] = True
        # Test Booleans
        self.assertEqual(
            self.rule._schema_check_primitive_type("True", ["boolean"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("False", ["boolean"]), False
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["boolean"]), False)
        # Test Strings
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["string"]), False)
        self.assertEqual(self.rule._schema_check_primitive_type(2, ["string"]), False)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["string"]), False
        )
        # Test Integer
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["integer"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["integer"]), False
        )
        # Test Double
        self.assertEqual(self.rule._schema_check_primitive_type("1", ["number"]), False)
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.2", ["number"]), False
        )
        self.assertEqual(self.rule._schema_check_primitive_type(1, ["number"]), True)
        self.assertEqual(
            self.rule._schema_check_primitive_type(True, ["number"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["number"]), False
        )
        # Test multiple types
        self.assertEqual(
            self.rule._schema_check_primitive_type("1", ["string", "integer"]), True
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("test", ["boolean", "integer"]),
            False,
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type(1.34, ["boolean", "string"]), False
        )
        self.assertEqual(
            self.rule._schema_check_primitive_type("1.34", ["boolean", "number"]), False
        )

        self.rule.config["strict"] = False


class TestResourceValuePrimitiveTypeJsonSchemaValidate(BaseRuleTestCase):
    """Test Primitive Value Types for Json Schema non strict"""

    def setUp(self):
        """Setup"""
        self.rule = ValuePrimitiveType()
        self.rule.config["strict"] = False

        self.validator = jsonschema._types.TypeChecker(
            {
                "any": jsonschema._types.is_any,
                "array": jsonschema._types.is_array,
                "boolean": jsonschema._types.is_bool,
                "integer": lambda checker, instance: (
                    jsonschema._types.is_integer(checker, instance)
                    or isinstance(instance, float)
                    and instance.is_integer()
                ),
                "object": jsonschema._types.is_object,
                "null": jsonschema._types.is_null,
                "number": jsonschema._types.is_number,
                "string": jsonschema._types.is_string,
            },
        )

    def test_validation(self):
        """Test Positive"""
        # sub is a string boolean
        self.assertEqual(
            len(
                list(
                    self.rule.validate(
                        self.validator, ["string"], {"Fn::Sub": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # split is an array
        self.assertEqual(
            len(
                list(
                    self.rule.validate(
                        self.validator, ["string"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            1,
        )
        # array type with split
        self.assertEqual(
            len(
                list(
                    self.rule.validate(
                        self.validator, ["array"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # two types the second being valid
        self.assertEqual(
            len(
                list(
                    self.rule.validate(
                        self.validator, ["string", "array"], {"Fn::Split": ["test"]}, {}
                    )
                )
            ),
            0,
        )
        # unknown function should return erro
        self.assertEqual(
            len(
                list(
                    self.rule.validate(
                        self.validator, ["string"], {"Fn::ABC": ["test"]}, {}
                    )
                )
            ),
            1,
        )
