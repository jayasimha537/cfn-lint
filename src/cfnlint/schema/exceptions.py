from jsonschema import exceptions

class ValidationError(exceptions.ValidationError):
    def __init__(self, message, extra_args=None):
        super().__init__(message)
        self.extra_args = extra_args or {}
