import hashlib
import pytest
from contract import BatchInput, SaveInput, SaveOutput, UserV2
from plugin.logic import pin_reference, read_dataset, save_candidate
from verifier import verify_input, verify_output, verify_task

@pytest.mark.parametrize('batch',['messy','international','empty'])
def test_gold(tmp_path,batch):
    task = BatchInput(batch)
    pin = pin_reference(task,tmp_path)
    read = read_dataset(task,tmp_path)
    assert verify_output('read_legacy_records',task,read,str(tmp_path))['valid']
    assert verify_output('pin_migration_truth',task,pin,str(tmp_path))['valid']
    candidate = SaveInput(batch,pin.expected)
    out = save_candidate(candidate,tmp_path)
    assert verify_output('save_migration',candidate,out,str(tmp_path))['valid']
    assert verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']

@pytest.mark.parametrize('problem', ['wrong_email','missing','duplicate','extra','wrong_bool','lost_zero'])
def test_wrong_migration(tmp_path,problem):
    task = BatchInput('messy'); pin = pin_reference(task,tmp_path)
    rows = list(pin.expected)
    if problem == 'wrong_email':
        r=rows[0];rows[0]=UserV2(r.user_id,r.display_name,'ADA@EXAMPLE.COM',r.enabled,r.postal_code,r.country_code)
    elif problem == 'missing': rows.pop()
    elif problem == 'duplicate': rows.append(rows[0])
    elif problem == 'extra': rows.append(UserV2(900,'extra','x',False,'123','US'))
    elif problem == 'wrong_bool':
        r=rows[1];rows[1]=UserV2(r.user_id,r.display_name,r.email,True,r.postal_code,r.country_code)
    elif problem == 'lost_zero':
        r=rows[0];rows[0]=UserV2(r.user_id,r.display_name,r.email,r.enabled,'501',r.country_code)
    out=save_candidate(SaveInput('messy',rows),tmp_path)
    assert not verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']

def test_reject_tampered_or_missing_file(tmp_path):
    task=BatchInput('empty');pin=pin_reference(task,tmp_path)
    out=save_candidate(SaveInput('empty',[]),tmp_path)
    (tmp_path/out.path).write_bytes(b'not json')
    assert not verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']
    out.digest=hashlib.sha256(b'not json').hexdigest()
    malformed_path = f'reports/result-{out.digest}.json'
    (tmp_path/out.path).rename(tmp_path/malformed_path)
    out.path = malformed_path
    assert not verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']
    (tmp_path/out.path).unlink()
    assert not verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']

def test_bad_input_and_reference(tmp_path):
    assert not verify_input('read_legacy_records',BatchInput('bad'))['valid']
    task=BatchInput('messy');pin=pin_reference(task,tmp_path)
    pin.expected[0].display_name = 'Wrong'
    out=save_candidate(SaveInput('messy',pin.expected),tmp_path)
    assert not verify_task('migrate-users',task,out,pin,str(tmp_path))['valid']
