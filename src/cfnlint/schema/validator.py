import attr
import reprlib
import typing
import warnings
from operator import methodcaller
import jsonschema
from jsonschema.validators import validator_for, RefResolver
from jsonschema import exceptions, validators
from typing import Mapping, Any, Union, Iterable

def _id_of(schema):
    """
    Return the ID of a schema for recent JSON Schema drafts.
    """
    if schema is True or schema is False:
        return ""
    return schema.get("$id", "")

def create(
    meta_schema,
    validators=(),
    version=None,
    type_checker=jsonschema._types.draft7_type_checker,
    format_checker=jsonschema._format.draft7_format_checker,
    id_of=_id_of,
    applicable_validators=methodcaller("items"),
):
    """
    Create a new validator class.
    Arguments:
        meta_schema (collections.abc.Mapping):
            the meta schema for the new validator class
        validators (collections.abc.Mapping):
            a mapping from names to callables, where each callable will
            validate the schema property with the given name.
            Each callable should take 4 arguments:
                1. a validator instance,
                2. the value of the property being validated within the
                   instance
                3. the instance
                4. the schema
        version (str):
            an identifier for the version that this validator class will
            validate. If provided, the returned validator class will
            have its ``__name__`` set to include the version, and also
            will have `jsonschema.validators.validates` automatically
            called for the given version.
        type_checker (jsonschema.TypeChecker):
            a type checker, used when applying the :kw:`type` keyword.
            If unprovided, a `jsonschema.TypeChecker` will be created
            with a set of default types typical of JSON Schema drafts.
        format_checker (jsonschema.FormatChecker):
            a format checker, used when applying the :kw:`format` keyword.
            If unprovided, a `jsonschema.FormatChecker` will be created
            with a set of default formats typical of JSON Schema drafts.
        id_of (collections.abc.Callable):
            A function that given a schema, returns its ID.
        applicable_validators (collections.abc.Callable):
            A function that given a schema, returns the list of
            applicable validators (validation keywords and callables)
            which will be used to validate the instance.
    Returns:
        a new `jsonschema.protocols.Validator` class
    """
    # preemptively don't shadow the `Validator.format_checker` local
    format_checker_arg = format_checker

    @attr.s
    class Validator():
        """
        The protocol to which all validator classes adhere.
        Arguments:
            schema:
                The schema that the validator object will validate with.
                It is assumed to be valid, and providing
                an invalid schema can lead to undefined behavior. See
                `Validator.check_schema` to validate a schema first.
            resolver:
                a resolver that will be used to resolve :kw:`$ref`
                properties (JSON references). If unprovided, one will be created.
            format_checker:
                if provided, a checker which will be used to assert about
                :kw:`format` properties present in the schema. If unprovided,
                *no* format validation is done, and the presence of format
                within schemas is strictly informational. Certain formats
                require additional packages to be installed in order to assert
                against instances. Ensure you've installed `jsonschema` with
                its `extra (optional) dependencies <index:extras>` when
                invoking ``pip``.
        """

        VALIDATORS = dict(validators)
        META_SCHEMA = dict(meta_schema)
        TYPE_CHECKER = type_checker
        FORMAT_CHECKER = format_checker_arg
        ID_OF = staticmethod(id_of)

        schema = attr.ib(repr=reprlib.repr)
        resolver = attr.ib(default=None, repr=False)
        format_checker = attr.ib(default=None)

        def __init__(
            self,
            schema: Mapping,
            resolver: Union[RefResolver, None] = None,
            format_checker: None = None,
        ) -> None:
            pass

        def __attrs_post_init__(self):
            if self.resolver is None:
                self.resolver = RefResolver.from_schema(
                    self.schema,
                    id_of=id_of,
                )

        @classmethod
        def check_schema(cls, schema: Mapping) -> None:
            pass

        def is_type(self, instance: Any, type: str) -> bool:
            """
            Check if the instance is of the given (JSON Schema) type.
            Arguments:
                instance:
                    the value to check
                type:
                    the name of a known (JSON Schema) type
            Returns:
                whether the instance is of the given type
            Raises:
                `jsonschema.exceptions.UnknownType`:
                    if ``type`` is not a known type
            """
            try:
                return self.TYPE_CHECKER.is_type(instance, type)
            except exceptions.UndefinedTypeCheck:
                raise exceptions.UnknownType(type, instance, self.schema)

        def is_valid(self, instance: Any) -> bool:
            """
            Check if the instance is valid under the current `schema`.
            Returns:
                whether the instance is valid or not
            >>> schema = {"maxItems" : 2}
            >>> Draft202012Validator(schema).is_valid([2, 3, 4])
            False
            """
            error = next(self.iter_errors(instance), None)
            return error is None

        def iter_errors(self, instance: Any) -> Iterable[exceptions.ValidationError]:
            r"""
            Lazily yield each of the validation errors in the given instance.
            >>> schema = {
            ...     "type" : "array",
            ...     "items" : {"enum" : [1, 2, 3]},
            ...     "maxItems" : 2,
            ... }
            >>> v = Draft202012Validator(schema)
            >>> for error in sorted(v.iter_errors([2, 3, 4]), key=str):
            ...     print(error.message)
            4 is not one of [1, 2, 3]
            [2, 3, 4] is too long
            .. deprecated:: v4.0.0
                Calling this function with a second schema argument is deprecated.
                Use `Validator.evolve` instead.
            """
            _schema = self.schema

            if _schema is True:
                return
            elif _schema is False:
                yield exceptions.ValidationError(
                    f"False schema does not allow {instance!r}",
                    validator=None,
                    validator_value=None,
                    instance=instance,
                    schema=_schema,
                )
                return

            scope = id_of(_schema)
            if scope:
                self.resolver.push_scope(scope)
            try:
                for k, v in applicable_validators(_schema):
                    validator = self.VALIDATORS.get(k)
                    if validator is None:
                        continue

                    errors = validator(self, v, instance, _schema) or ()
                    for error in errors:
                        # set details if not already set by the called fn
                        if error is None:
                            continue
                        error._set(
                            validator=k,
                            validator_value=v,
                            instance=instance,
                            schema=_schema,
                            type_checker=self.TYPE_CHECKER,
                        )
                        if k not in {"if", "$ref"}:
                            error.schema_path.appendleft(k)
                        yield error
            finally:
                if scope:
                    self.resolver.pop_scope()

        def validate(self, instance: Any) -> None:
            """
            Check if the instance is valid under the current `schema`.
            Raises:
                `jsonschema.exceptions.ValidationError`:
                    if the instance is invalid
            >>> schema = {"maxItems" : 2}
            >>> Draft202012Validator(schema).validate([2, 3, 4])
            Traceback (most recent call last):
                ...
            ValidationError: [2, 3, 4] is too long
            """
            for error in self.iter_errors(instance):
                raise error

        def evolve(self, **kwargs) -> "Validator":
            """
            Create a new validator like this one, but with given changes.
            Preserves all other attributes, so can be used to e.g. create a
            validator with a different schema but with the same :kw:`$ref`
            resolution behavior.
            >>> validator = Draft202012Validator({})
            >>> validator.evolve(schema={"type": "number"})
            Draft202012Validator(schema={'type': 'number'}, format_checker=None)
            The returned object satisfies the validator protocol, but may not
            be of the same concrete class! In particular this occurs
            when a :kw:`$ref` occurs to a schema with a different
            :kw:`$schema` than this one (i.e. for a different draft).
            >>> validator.evolve(
            ...     schema={"$schema": Draft7Validator.META_SCHEMA["$id"]}
            ... )
            Draft7Validator(schema=..., format_checker=None)
            """
            cls = self.__class__

            schema = kwargs.setdefault("schema", self.schema)
            NewValidator = validator_for(schema, default=cls)

            for field in attr.fields(cls):
                if not field.init:
                    continue
                attr_name = field.name  # To deal with private attributes.
                init_name = attr_name if attr_name[0] != "_" else attr_name[1:]
                if init_name not in kwargs:
                    kwargs[init_name] = getattr(self, attr_name)

            return NewValidator(**kwargs)

        def descend(self, instance, schema, path=None, schema_path=None):
            for error in self.evolve(schema=schema).iter_errors(instance):
                if path is not None:
                    error.path.appendleft(path)
                if schema_path is not None:
                    error.schema_path.appendleft(schema_path)
                yield

    return Validator