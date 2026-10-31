"""Pure verifier derives migration from pinned legacy records without calling plugin logic."""
from contract import Tool
from .checks import result, read_receipt

BATCHES = ('messy','international','empty')

def convert(records):
    output = {}
    for user in records:
        if user.id in output or user.id < 0 or user.active.strip().lower() not in ('yes','true','1','no','false','0'):
            return None
        output[user.id] = {'user_id': user.id,
                           'display_name': ' '.join(user.full_name.split()),
                           'email': user.email.strip().lower(),
                           'enabled': user.active.strip().lower() in ('yes','true','1'),
                           'postal_code': user.zip.strip(),
                           'country_code': user.country.strip().upper() or 'US'}
    return output

def consistent(records, expected):
    found = {}
    for rec in records:
        if not isinstance(rec, dict) or set(rec) != {'user_id','display_name','email','enabled','postal_code','country_code'}:
            return False
        key = rec['user_id']
        if type(key) is not int or key in found or type(rec['enabled']) is not bool:
            return False
        if any(not isinstance(rec[x],str) for x in ('display_name','email','postal_code','country_code')):
            return False
        found[key] = rec
    return found == expected

def _record(row):
    return {'user_id': row.user_id, 'display_name': row.display_name, 'email': row.email,
            'enabled': row.enabled, 'postal_code':row.postal_code,'country_code':row.country_code}

def verify_input(tool, value):
    ok = value.batch in BATCHES
    if tool == Tool.SAVE:
        ok = ok and len(value.records) <= 500
    return result(ok, 'valid batch' if ok else 'unknown batch or oversized output')

def verify_output(tool, input_value, output_value, workspace):
    if tool == Tool.READ:
        return result(output_value.batch == input_value.batch and convert(output_value.records) is not None, 'read legacy records')
    if tool == Tool.PIN:
        oracle = convert(output_value.records)
        valid = output_value.batch == input_value.batch and oracle is not None and consistent([_record(x) for x in output_value.expected],oracle)
        return result(valid, 'reference independently consistent' if valid else 'invalid reference')
    saved, problem = read_receipt(workspace, output_value)
    expected = {'batch': input_value.batch,'records':[_record(x) for x in input_value.records]}
    ok = not problem and output_value.batch == input_value.batch and output_value.count == len(input_value.records) and saved == expected
    return result(ok, 'migration saved' if ok else problem or 'report differs from supplied records')

def verify_task(arguments, output, reference, workspace):
    if reference is None or arguments.batch != reference.batch or arguments.batch != output.batch:
        return result(False, 'missing or wrong pinned legacy batch')
    oracle = convert(reference.records)
    if oracle is None or not consistent([_record(x) for x in reference.expected], oracle):
        return result(False, 'reference migration inconsistent')
    saved, problem = read_receipt(workspace, output)
    if problem:
        return result(False, problem)
    if saved.get('batch') != arguments.batch or not isinstance(saved.get('records'), list):
        return result(False, 'invalid saved migration shape or batch')
    if len(saved['records']) != output.count:
        return result(False,'record count mismatch')
    if not consistent(saved['records'], oracle):
        return result(False,'incorrect data, field types, duplicate IDs, missing or extra users')
    return result(True,'all migrated fields and types match independently computed reference', users=len(oracle))
