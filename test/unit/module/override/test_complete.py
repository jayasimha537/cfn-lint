"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase

from cfnlint.rules import RulesCollection
from cfnlint.rules.resources.Configuration import Configuration  # pylint: disable=E0401
from cfnlint.rules.resources.properties.JsonSchema import JsonSchema
from cfnlint.rules.resources.properties.Required import (
    Required,  # pylint: disable=E0401
)
from cfnlint.runner import Runner
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.schema.patch import SchemaPatch


class TestComplete(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.collection.register(JsonSchema())
        self.collection.register(Configuration())
        self.collection.register(Required())
        self.region = "us-east-1"

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        PROVIDER_SCHEMA_MANAGER.reset()

    def test_success_run(self):
        """Success test"""
        filename = "test/fixtures/templates/good/override/complete.yaml"
        template = self.load_template(filename)

        with open("test/fixtures/templates/override_spec/complete.json") as fp:
            p = json.load(fp)
            schema_patch = SchemaPatch.from_dict(p)

        PROVIDER_SCHEMA_MANAGER._patch(schema_patch, region=self.region)

        good_runner = Runner(self.collection, filename, template, [self.region], [])
        self.assertEqual([], good_runner.run())

    def test_fail_run(self):
        """Failure test required"""
        filename = "test/fixtures/templates/bad/override/complete.yaml"
        template = self.load_template(filename)

        with open("test/fixtures/templates/override_spec/complete.json") as fp:
            p = json.load(fp)
            schema_patch = SchemaPatch.from_dict(p)

        PROVIDER_SCHEMA_MANAGER._patch(schema_patch, region=self.region)

        bad_runner = Runner(self.collection, filename, template, [self.region], [])
        errs = bad_runner.run()
        self.assertEqual(3, len(errs))
