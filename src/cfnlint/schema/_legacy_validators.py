from jsonschema import _utils
from jsonschema.exceptions import ValidationError


def id_of_ignore_ref(property="$id"):
    def id_of(schema):
        """
        Ignore an ``$id`` sibling of ``$ref`` if it is present.
        Otherwise, return the ID of the given schema.
        """
        if schema is True or schema is False or "$ref" in schema:
            return ""
        return schema.get(property, "")
    return id_of


def ignore_ref_siblings(schema):
    """
    Ignore siblings of ``$ref`` if it is present.
    Otherwise, return all keywords.
    Suitable for use with `create`'s ``applicable_validators`` argument.
    """
    ref = schema.get("$ref")
    if ref is not None:
        return [("$ref", ref)]
    else:
        return schema.items()

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
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependencies.items():
        if property not in instance:
            continue

        if validator.is_type(dependency, "array"):
            for each in dependency:
                if each not in instance:
                    message = f"{each!r} is a dependency of {property!r}"
                    yield ValidationError(message)
        else:
            yield from validator.descend(
                instance, dependency, schema_path=property,
            )

def items_draft6_draft7_draft201909(validator, items, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if validator.is_type(items, "array"):
        for (index, item), subschema in zip(enumerate(instance), items):
            yield from validator.descend(
                item, subschema, path=index, schema_path=index,
            )
    else:
        for index, item in enumerate(instance):
            yield from validator.descend(item, items, path=index)

def contains_draft6_draft7(validator, contains, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if not any(
        validator.evolve(schema=contains).is_valid(element)
        for element in instance
    ):
        yield ValidationError(
            f"None of {instance!r} are valid under the given schema",
        )