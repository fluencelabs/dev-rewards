from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Dict


@dataclass_json
@dataclass
class Metadata:
    root: str
    addresses: List[str]
    encryptedKeys: Dict[str, Dict[str, str]]

