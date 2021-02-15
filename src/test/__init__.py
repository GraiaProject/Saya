
from dataclasses import dataclass
from graia.saya.schema import BaseSchema

@dataclass(init=True)
class TestSchema(BaseSchema):
    test_name: str