"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Originally taken from https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_validators.py
and https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_legacy_validators.py
adapted for CloudFormation usage
"""

import re
from fractions import Fraction
from urllib.parse import urldefrag, urljoin

from jsonschema._utils import (
    ensure_list,
    equal,
    extras_msg,
    find_additional_properties,
    find_evaluated_item_indexes_by_schema,
    find_evaluated_property_keys_by_schema,
    unbool,
    uniq,
)

from cfnlint.jsonschema.exceptions import ValidationError


def id_of_ignore_ref(prop="$id"):
    def id_of(schema):
        """
        Ignore an ``$id`` sibling of ``$ref`` if it is present.
        Otherwise, return the ID of the given schema.
        """
        if schema is True or schema is False or "$ref" in schema:
            return ""
        return schema.get(prop, "")

    return id_of


def ignore_ref_siblings(schema):
    """
    Ignore siblings of ``$ref`` if it is present.
    Otherwise, return all keywords.
    Suitable for use with `create`'s ``applicable_validators`` argument.
    """
    ref_link = schema.get("$ref")
    if ref_link is not None:
        return [("$ref", ref_link)]

    return schema.items()


# pylint: disable=unused-argument
def dependencies_draft4_draft6_draft7(
    validator,
    dependencies,
    instance,
    schema,
):
    """
    Support for the ``dependencies`` keyword from pre-draft 2019-09.
    In later drafts, the keyword was split into separate
    ``dependentRequired`` and ``dependentSchemas`` validators.
    """


def contains_draft6_draft7(validator, cs, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if not any(validator.evolve(schema=cs).is_valid(element) for element in instance):
        yield ValidationError(
            f"None of {instance!r} are valid under the given schema",
        )


# pylint: disable=unused-argument
def items_draft6_draft7_draft201909(validator, iS, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if validator.is_type(iS, "array"):
        for (index, item), subschema in zip(enumerate(instance), iS):
            yield from validator.descend(
                item,
                subschema,
                path=index,
                schema_path=index,
            )
    else:
        for index, item in enumerate(instance):
            yield from validator.descend(item, iS, path=index)


# pylint: disable=unused-argument
def patternProperties(validator, pProps, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for _pattern, subschema in pProps.items():
        for k, v in instance.items():
            if re.search(_pattern, k):
                yield from validator.descend(
                    v,
                    subschema,
                    path=k,
                    schema_path=_pattern,
                )


# pylint: disable=unused-argument
def propertyNames(validator, pNames, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for prop in instance:
        yield from validator.descend(instance=prop, schema=pNames)


def additionalProperties(validator, aP, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    extras = set(find_additional_properties(instance, schema))

    if validator.is_type(aP, "object"):
        for extra in extras:
            yield from validator.descend(instance[extra], aP, path=extra)
    elif not aP and extras:
        if "patternProperties" in schema:
            if len(extras) == 1:
                verb = "does"
            else:
                verb = "do"

            joined = ", ".join(repr(each) for each in sorted(extras))
            patterns = ", ".join(
                repr(each) for each in sorted(schema["patternProperties"])
            )
            error = f"{joined} {verb} not match any of the regexes: {patterns}"
            yield ValidationError(error)
        else:
            for extra in extras:
                error = "Additional properties are not allowed (%s unexpected)"
                yield ValidationError(error % extra, path=[extra])


def items(validator, iS, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    prefix = len(schema.get("prefixItems", []))
    total = len(instance)
    if iS is False and total > prefix:
        message = f"Expected at most {prefix} items, but found {total}"
        yield ValidationError(message)
    else:
        for index in range(prefix, total):
            yield from validator.descend(
                instance=instance[index],
                schema=iS,
                path=index,
            )


def additionalItems(validator, aI, instance, schema):
    if not validator.is_type(instance, "array") or validator.is_type(
        schema.get("items", {}), "object"
    ):
        return

    len_items = len(schema.get("items", []))
    if validator.is_type(aI, "object"):
        for index, item in enumerate(instance[len_items:], start=len_items):
            yield from validator.descend(item, aI, path=index)
    elif not aI and len(instance) > len(schema.get("items", [])):
        error = "Additional items are not allowed (%s %s unexpected)"
        yield ValidationError(
            error % extras_msg(instance[len(schema.get("items", [])) :]),
        )


# pylint: disable=unused-argument
def const(validator, c, instance, schema):
    if not equal(instance, c):
        yield ValidationError(f"{c!r} was expected")


def contains(validator, cS, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    matches = 0
    min_contains = schema.get("minContains", 1)
    max_contains = schema.get("maxContains", len(instance))

    for each in instance:
        if validator.evolve(schema=cS).is_valid(each):
            matches += 1
            if matches > max_contains:
                yield ValidationError(
                    "Too many items match the given schema "
                    f"(expected at most {max_contains})",
                    validator="maxContains",
                    validator_value=max_contains,
                )
                return

    if matches < min_contains:
        if not matches:
            yield ValidationError(
                f"{instance!r} does not contain items " "matching the given schema",
            )
        else:
            yield ValidationError(
                "Too few items match the given schema (expected at least "
                f"{min_contains} but only {matches} matched)",
                validator="minContains",
                validator_value=min_contains,
            )


# pylint: disable=unused-argument
def exclusiveMinimum(validator, m, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance <= m:
        yield ValidationError(
            f"{instance!r} is less than or equal to " f"the minimum of {m!r}",
        )


# pylint: disable=unused-argument
def exclusiveMaximum(validator, m, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance >= m:
        yield ValidationError(
            f"{instance!r} is greater than or equal " f"to the maximum of {m!r}",
        )


# pylint: disable=unused-argument
def minimum(validator, m, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance < m:
        message = f"{instance!r} is less than the minimum of {m!r}"
        yield ValidationError(message)


# pylint: disable=unused-argument
def maximum(validator, m, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance > m:
        message = f"{instance!r} is greater than the maximum of {m!r}"
        yield ValidationError(message)


# pylint: disable=unused-argument
def multipleOf(validator, dB, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if isinstance(dB, float):
        quotient = instance / dB
        try:
            failed = int(quotient) != quotient
        except OverflowError:
            # When `instance` is large and `dB` is less than one,
            # quotient can overflow to infinity; and then casting to int
            # raises an error.
            #
            # In this case we fall back to Fraction logic, which is
            # exact and cannot overflow.  The performance is also
            # acceptable: we try the fast all-float option first, and
            # we know that fraction(dB) can have at most a few hundred
            # digits in each part.  The worst-case slowdown is therefore
            # for already-slow enormous integers or Decimals.
            failed = (Fraction(instance) / Fraction(dB)).denominator != 1
    else:
        failed = instance % dB

    if failed:
        yield ValidationError(f"{instance!r} is not a multiple of {dB}")


# pylint: disable=unused-argument
def minItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) < mI:
        yield ValidationError(f"{instance!r} is too short")


# pylint: disable=unused-argument
def maxItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) > mI:
        yield ValidationError(f"{instance!r} is too long")


# pylint: disable=unused-argument
def uniqueItems(validator, uI, instance, schema):
    if uI and validator.is_type(instance, "array") and not uniq(instance):
        yield ValidationError(f"{instance!r} has non-unique elements")


# pylint: disable=unused-argument
def pattern(validator, patrn, instance, schema):
    if validator.is_type(instance, "string") and not re.search(patrn, instance):
        yield ValidationError(f"{instance!r} does not match {patrn!r}")


# pylint: disable=unused-argument
def minLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) < mL:
        yield ValidationError(f"{instance!r} is too short")


# pylint: disable=unused-argument
def maxLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) > mL:
        yield ValidationError(f"{instance!r} is too long")


# pylint: disable=unused-argument
def dependentRequired(validator, dR, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for prop, dependency in dR.items():
        if prop not in instance:
            continue

        for each in dependency:
            if each not in instance:
                message = f"{each!r} is a dependency of {prop!r}"
                yield ValidationError(message)


# pylint: disable=unused-argument
def dependentSchemas(validator, dSchemas, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for prop, dependency in dSchemas.items():
        if prop not in instance:
            continue
        yield from validator.descend(
            instance,
            dependency,
            schema_path=prop,
        )


# pylint: disable=unused-argument
def enum(validator, enums, instance, schema):
    if instance in (0, 1):
        unbooled = unbool(instance)
        if all(unbooled != unbool(each) for each in enums):
            yield ValidationError(f"{instance!r} is not one of {enums!r}")
    elif instance not in enums:
        yield ValidationError(f"{instance!r} is not one of {enums!r}")


# pylint: disable=unused-argument
def ref(validator, r, instance, schema):
    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(r) as resolved:
            yield from validator.descend(instance, resolved)
    else:
        scope, resolved = validator.resolver.resolve(r)
        validator.resolver.push_scope(scope)

        try:
            yield from validator.descend(instance, resolved)
        finally:
            validator.resolver.pop_scope()


# pylint: disable=unused-argument
def dynamicRef(validator, dR, instance, schema):
    _, fragment = urldefrag(dR)

    # pylint: disable=protected-access
    for url in validator.resolver._scopes_stack:
        lookup_url = urljoin(url, dR)
        with validator.resolver.resolving(lookup_url) as subschema:
            if (
                "$dynamicAnchor" in subschema
                and fragment == subschema["$dynamicAnchor"]
            ):
                yield from validator.descend(instance, subschema)
                break
    else:
        with validator.resolver.resolving(dR) as subschema:
            yield from validator.descend(instance, subschema)


# pylint: disable=unused-argument,redefined-builtin
def type(validator, tS, instance, schema):
    tS = ensure_list(tS)

    if not any(validator.is_type(instance, type) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


# pylint: disable=unused-argument
def properties(validator, props, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for prop, subschema in props.items():
        if prop in instance:
            yield from validator.descend(
                instance[prop],
                subschema,
                path=prop,
                schema_path=prop,
            )


# pylint: disable=unused-argument
def required(validator, r, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    for prop in r:
        if prop not in instance:
            yield ValidationError(f"{prop!r} is a required property")


# pylint: disable=unused-argument
def minProperties(validator, mP, instance, schema):
    if validator.is_type(instance, "object") and len(instance) < mP:
        yield ValidationError(f"{instance!r} does not have enough properties")


# pylint: disable=unused-argument
def maxProperties(validator, mP, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    if validator.is_type(instance, "object") and len(instance) > mP:
        yield ValidationError(f"{instance!r} has too many properties")


# pylint: disable=unused-argument
def allOf(validator, aO, instance, schema):
    for index, subschema in enumerate(aO):
        yield from validator.descend(instance, subschema, schema_path=index)


# pylint: disable=unused-argument
def anyOf(validator, aO, instance, schema):
    all_errors = []
    for index, subschema in enumerate(aO):
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            f"{instance!r} is not valid under any of the given schemas",
            context=all_errors,
        )


# pylint: disable=unused-argument
def oneOf(validator, oO, instance, schema):
    subschemas = enumerate(oO)
    all_errors = []
    for index, subschema in subschemas:
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            f"{instance!r} is not valid under any of the given schemas",
            context=all_errors,
        )

    more_valid = [
        each
        for _, each in subschemas
        if validator.evolve(schema=each).is_valid(instance)
    ]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        yield ValidationError(f"{instance!r} is valid under each of {reprs}")


# pylint: disable=unused-argument
def not_(validator, not_schema, instance, schema):
    if validator.evolve(schema=not_schema).is_valid(instance):
        message = f"{instance!r} should not be valid under {not_schema!r}"
        yield ValidationError(message)


def if_(validator, if_schema, instance, schema):
    if validator.evolve(schema=if_schema).is_valid(instance):
        if "then" in schema:
            then = schema["then"]
            yield from validator.descend(instance, then, schema_path="then")
    elif "else" in schema:
        else_ = schema["else"]
        yield from validator.descend(instance, else_, schema_path="else")


# pylint: disable=unused-argument
def unevaluatedItems(validator, uItems, instance, schema):
    if not validator.is_type(instance, "array"):
        return
    evaluated_item_indexes = find_evaluated_item_indexes_by_schema(
        validator,
        instance,
        schema,
    )
    uItems = [
        item
        for index, item in enumerate(instance)
        if index not in evaluated_item_indexes
    ]
    if uItems:
        error = "Unevaluated items are not allowed (%s %s unexpected)"
        yield ValidationError(error % extras_msg(uItems))


def unevaluatedProperties(validator, uProps, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    evaluated_keys = find_evaluated_property_keys_by_schema(
        validator,
        instance,
        schema,
    )
    unevaluated_keys = []
    for prop in instance:
        if prop not in evaluated_keys:
            for _ in validator.descend(
                instance[prop],
                uProps,
                path=prop,
                schema_path=prop,
            ):
                unevaluated_keys.append(prop)

    if unevaluated_keys:
        if uProps is False:
            error = "Unevaluated properties are not allowed (%s %s unexpected)"
            yield ValidationError(error % extras_msg(unevaluated_keys))
        else:
            error = (
                "Unevaluated properties are not valid under "
                "the given schema (%s %s unevaluated and invalid)"
            )
            yield ValidationError(error % extras_msg(unevaluated_keys))


# pylint: disable=unused-argument
def prefixItems(validator, pItems, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    for (index, item), subschema in zip(enumerate(instance), pItems):
        yield from validator.descend(
            instance=item,
            schema=subschema,
            schema_path=index,
            path=index,
        )
