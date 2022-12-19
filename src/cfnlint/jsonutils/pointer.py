from typing import Sequence, Mapping


def resolve(obj, parts):
    """Resolves the pointer against obj and returns the referenced object"""

    for part in parts.split("/")[1:]:
        try:
            obj = walk(obj, part)
        except KeyError as e:
            raise e

    return obj


def get_part(doc, part):
        """Returns the next step in the correct type"""

        if isinstance(doc, Mapping):
            return part

        elif isinstance(doc, Sequence):

            if part == '-':
                return part

            return int(part)

        elif hasattr(doc, '__getitem__'):
            # Allow indexing via ducktyping
            # if the target has defined __getitem__
            return part

        else:
            raise KeyError("Document '%s' does not support indexing, "
                                       "must be mapping/sequence or support __getitem__" % type(doc))

def walk(obj, part):
    """ Walks one step in doc and returns the referenced part """

    part = get_part(obj, part)

    assert hasattr(obj, '__getitem__'), "invalid document type %s" % (type(obj),)

    if isinstance(obj, Sequence):
        try:
            return obj[part]

        except IndexError:
            raise KeyError("index '%s' is out of bounds" % (part, ))

    try:
        return obj[part]

    except KeyError as e:
        raise e