from typing import Dict, Mapping, Sequence, Union


def resolve_pointer(obj, pointer) -> Dict:
    """Find the elements at the end of a Cfn pointer

    Args:
        obj (dict): the root schema used for searching for the pointer
        pointer (str): the pointer using / to separate levels
    Returns:
        Dict: returns the object from the pointer
    """
    json_pointer = SchemaPointer(obj, pointer)
    return json_pointer.resolve()


class SchemaPointer:
    def __init__(self, obj: dict, pointer: str) -> None:
        self.obj = obj
        self.parts = pointer.split("/")[1:]

    def resolve(self) -> Dict:
        """Find the elements at the end of a Cfn pointer

        Args:
        Returns:
            Dict: returns the object from the pointer
        """
        obj = self.obj
        for part in self.parts:
            try:
                obj = self.walk(obj, part)
            except KeyError as e:
                raise e

        return obj

    def get_part(self, doc: Dict, part: str) -> Union[str, int]:
        """Returns the next step in the correct type

        Args:
            doc (dict): the object to evaluate for the part
            part (str): the string representation of the part
        Returns:
            str, int: returns the updated part
        """

        if isinstance(doc, Mapping):
            return part

        elif isinstance(doc, Sequence):

            if part == "-":
                return part

            return int(part)

        elif hasattr(doc, "__getitem__"):
            return part

        else:
            raise KeyError(
                "Document '%s' does not support indexing, "
                "must be mapping/sequence or support __getitem__" % type(doc)
            )

    def walk(self, obj: Dict, part: str) -> Dict:
        """Walks one step in doc and returns the referenced part

        Args:
            obj (dict): the object to evaluate for the part
            part (str): the string representation of the part
        Returns:
            Dict: returns the object at the part
        """

        part = self.get_part(obj, part)
        assert hasattr(obj, "__getitem__"), "invalid document type %s" % (type(obj),)

        if isinstance(obj, Sequence):
            try:
                return obj[part]

            except IndexError:
                raise KeyError("index '%s' is out of bounds" % (part,))

        try:
            # using a test for typeName as that is a root schema property
            if part == "properties" and obj.get("typeName"):
                return obj[part]
            if (
                obj.get("properties")
                and part != "definitions"
                and not obj.get("typeName")
            ):
                return obj["properties"][part]
            # arrays have a * in the path
            if part == "*" and obj.get("type") == "array":
                return obj.get("items")
            return obj[part]

        except KeyError as e:
            # CFN JSON pointers can go down $ref paths so lets do that if we can
            if obj.get("$ref"):
                try:
                    return resolve_pointer(self.obj, f"{obj.get('$ref')}/{part}")
                except KeyError as e:
                    raise e
            raise e
