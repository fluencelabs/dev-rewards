from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Metadata:
    root: str
    addresses: list[str]
    encryptedKeys: dict[str, dict[str, str]]
