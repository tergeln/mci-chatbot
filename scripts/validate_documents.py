import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
required = {'document_id','doc_type','title','status','version','valid_from','valid_to','lang','course_id','source_name','sections'}
allowed = {'draft','approved','test_only','archived'}
count=0
for path in sorted((ROOT/'data/documents').glob('*.json')):
    obj=json.loads(path.read_text(encoding='utf-8'))
    assert not (required-set(obj)), f'{path}: missing {required-set(obj)}'
    assert obj['status'] in allowed, f'{path}: invalid status'
    assert isinstance(obj['sections'],list) and obj['sections'],f'{path}: empty sections'
    for section in obj['sections']:
        assert {'section_id','heading','page','content'} <= section.keys(),f'{path}: invalid section'
        assert section['content'].strip(),f'{path}: empty content'
    count+=1
for line in (ROOT/'data/golden_set/questions.jsonl').read_text(encoding='utf-8').splitlines():
    if line.strip():
        obj=json.loads(line)
        assert {'id','query','category','expected_action','review_status'} <= obj.keys()
print(f'OK: {count} documents + golden set JSONL validated')
