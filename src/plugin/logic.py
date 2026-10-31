"""Independent migrator and writable report tool."""
from pathlib import Path
from dataclasses import asdict
from contract import BatchInput, LegacyUser, UserV2, ReadOutput, ReferenceOutput, SaveInput, SaveOutput
from plugin.datasets import FIXTURES, RULES
from plugin.storage import store

def _data(batch):
    if batch not in FIXTURES:
        raise ValueError("unknown batch; choose messy, international, empty")
    return [LegacyUser(**r) for r in FIXTURES[batch]]

def _convert(user):
    return UserV2(user.id, ' '.join(user.full_name.split()), user.email.strip().lower(),
                  user.active.strip().lower() in ('yes', 'true', '1'), user.zip.strip(),
                  user.country.strip().upper() or 'US')

def read_dataset(input: BatchInput, workspace: Path) -> ReadOutput:
    return ReadOutput(input.batch, _data(input.batch), RULES)

def pin_reference(input: BatchInput, workspace: Path) -> ReferenceOutput:
    original = _data(input.batch)
    return ReferenceOutput(input.batch, original, [_convert(row) for row in original])

def save_candidate(input: SaveInput, workspace: Path) -> SaveOutput:
    _data(input.batch)
    if len(input.records) > 500:
        raise ValueError('too many records')
    path, digest = store(workspace, {'batch': input.batch, 'records': [asdict(r) for r in input.records]})
    return SaveOutput(input.batch, path, digest, len(input.records))
