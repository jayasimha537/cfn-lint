from __future__ import annotations


class ResourceNotFoundError(Exception):
    def __init__(self, resource_type: str, region: str):
        super().__init__(f"Resource type '{resource_type}' is not found in '{region}'")
