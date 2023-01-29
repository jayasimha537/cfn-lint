"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import cfnlint.helpers
from cfnlint.helpers import REGISTRY_SCHEMAS
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError
from jsonschema import Draft7Validator
from jsonschema.validators import extend
from cfnlint.helpers import load_resource
from cfnlint.data.AdditionalSpecs.schema import resource
from cfnlint.schema.exceptions import ValidationError


class Configuration(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__()
        schema = cfnlint.helpers.load_resource(resource, "configuration.json")
        self.regions = []
        self.validator = extend(
            validator=Draft7Validator,
            validators={
                "cfnType": self._cfnType,
                "cfnPropertiesRequired": self._cfnPropertiesRequired
            },
        )(schema=schema)

    def initialize(self, cfn):
        super().initialize(cfn)
        self.regions = cfn.regions

    def _cfnType(self, validator, iT, instance, schema):
        if not validator.is_type(instance, "string"):
            return
        for region in self.regions:
            if instance in PROVIDER_SCHEMA_MANAGER.get_resource_types(region=region):
                continue
            if not instance.startswith(
                ("Custom::", "AWS::Serverless::")
            ) and not instance.endswith("::MODULE"):
                yield ValidationError(
                    f"Resource type `{instance}` does not exist in '{region}'"
                )

    def _cfnPropertiesRequired(self, validator, pR, instance, schema):
        r_type = instance.get("Type")
        # validated someplace else
        if not validator.is_type(r_type, "string"):
            return
        for region in self.regions:
            try:
                schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(region=region, resource_type=r_type)
                if schema.json_schema().get("required", []):
                    if (
                        r_type == "AWS::CloudFormation::WaitCondition"
                        and "CreationPolicy" in instance.keys()
                    ):
                        self.logger.debug(
                            "Exception to required properties section as CreationPolicy is defined."
                        )
                    elif "Properties" not in instance:
                        yield ValidationError(
                            f"Resource type `{r_type}` has required properties"
                        )
            except ResourceNotFoundError:
                continue

    def _check_resource(self, cfn, resource_name, resource_values):
        """Check Resource"""
        matches = []

        for e in self.validator.iter_errors(instance=resource_values):
            kwargs = {}
            e_path = ["Resources", resource_name] + list(e.path)
            if len(e.path) > 0:
                e_path_override = getattr(e, "path_override", None)
                if e_path_override:
                    e_path = list(e.path_override)
                else:
                    key = e.path[-1]
                    if hasattr(key, "start_mark"):
                        kwargs["location"] = (
                            key.start_mark.line,
                            key.start_mark.column,
                            key.end_mark.line,
                            key.end_mark.column,
                        )

            matches.append(
                RuleMatch(
                    e_path,
                    e.message,
                    **kwargs,
                )
            )

        return matches

    def match(self, cfn):
        matches = []

        resources = cfn.template.get("Resources", {})
        if not isinstance(resources, dict):
            message = "Resource not properly configured"
            matches.append(RuleMatch(["Resources"], message))
        else:
            for resource_name, resource_values in cfn.template.get(
                "Resources", {}
            ).items():
                self.logger.debug(
                    "Validating resource %s base configuration", resource_name
                )
                matches.extend(
                    self._check_resource(cfn, resource_name, resource_values)
                )

        return matches
