"""Typed contracts for legacy user migration."""
from dataclasses import dataclass
from enum import Enum
from typing import Annotated
from slimconfig import Output

class Tool(Enum):
    PIN = "pin_migration_truth"
    READ = "read_legacy_records"
    SAVE = "save_migration"

class Task(Enum):
    MAIN = "migrate-users"

@dataclass
class BatchInput(Output):
    batch: Annotated[str, "Legacy batch: messy, international, or empty"]

@dataclass
class LegacyUser(Output):
    id: int
    full_name: str
    email: str
    active: str
    zip: str
    country: str

@dataclass
class UserV2(Output):
    user_id: int
    display_name: str
    email: str
    enabled: bool
    postal_code: str
    country_code: str

@dataclass
class ReadOutput(Output):
    batch: str
    records: list[LegacyUser]
    rules: str

@dataclass
class ReferenceOutput(Output):
    batch: str
    records: list[LegacyUser]
    expected: list[UserV2]

@dataclass
class SaveInput(Output):
    batch: str
    records: Annotated[list[UserV2], "All migrated records, with exact destination field names and types"]

@dataclass
class SaveOutput(Output):
    batch: str
    path: str
    digest: str
    count: int

TOOLS = {Tool.PIN: (BatchInput, ReferenceOutput), Tool.READ: (BatchInput, ReadOutput), Tool.SAVE: (SaveInput, SaveOutput)}
TASKS = {Task.MAIN: (BatchInput, SaveOutput)}
