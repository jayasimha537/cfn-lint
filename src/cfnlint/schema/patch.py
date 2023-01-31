from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SchemaPatch:
    included_resource_types: List[str]
    excluded_resource_types: List[str]
    patches: Dict[str, List[Dict]]
    
    @staticmethod
    def from_dict(value: Dict):
        return SchemaPatch(
            included_resource_types=value.get("IncludeResourceTypes", []),
            excluded_resource_types=value.get("ExcludeResourceTypes", []),
            patches=value.get("Patches", {})
        )

