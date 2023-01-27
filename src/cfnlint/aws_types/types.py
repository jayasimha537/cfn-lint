from cfnlint.template.template import Template
from typing import List

class AwsType():

    def __init__(self, ref: List, getatt) -> None:
        self.ref = ref

    def validiate_ref(self, ref: str):



class AwsTypes():

    def __init__(self, cfn: Template) -> None:
        pass

    def availability_zones(self) -> None:
        
