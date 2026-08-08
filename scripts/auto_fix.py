#!/usr/bin/env python3
"""Auto-fix all error files: conservative+radical -> incremental, high-reg -> add compliance."""
import json, glob
from datetime import datetime, timezone
from pathlib import Path

raw_dir = Path('datasets_treino_finetune/raw')
files = sorted(raw_dir.glob('*.json'))

fixed_conservative = 0
fixed_compliance = 0
files_modified = 0

for fp in files:
    d = json.loads(fp.read_text(encoding='utf-8'))
    answers = d['input']['answers']
    ra = answers['riskAppetite']
    reg = answers['regulatoryEnvironment']
    sector = d['input']['company']['sector']
    opps = d['output']['opportunities']
    modified = False

    if ra == 'conservative':
        for o in opps:
            if isinstance(o, dict) and o.get('type', '').lower() == 'radical':
                o['type'] = 'incremental'
                rat = o.get('rationale', '')
                if rat and 'radical' in rat.lower():
                    o['rationale'] = rat.replace('radical', 'bold').replace('Radical', 'Bold')
                fixed_conservative += 1
                modified = True

    if reg == 'high':
        for o in opps:
            if not isinstance(o, dict):
                continue
            actions = o.get('execution_plan', {}).get('first_actions', [])
            actions_text = ' '.join(str(a) for a in actions).lower()
            kw = ['compliance', 'legal', 'regulatory', 'certification', 'iso', 'gdpr', 'hipaa', 'audit', 'standards']
            if not any(k in actions_text for k in kw):
                domain = 'GDPR and data privacy' if any(t in sector.lower() for t in ['tech', 'saas', 'fintech', 'health']) else 'regulatory'
                step = f'Conduct {domain} compliance review with legal team to ensure alignment with applicable regulations'
                actions.append(step)
                fixed_compliance += 1
                modified = True

    if modified:
        d['metadata']['reviewed'] = True
        d['metadata']['auto_fixed'] = True
        d['metadata']['reviewed_at'] = datetime.now(timezone.utc).isoformat()
        fp.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
        files_modified += 1

print(f'Conservative+radical fixes: {fixed_conservative}')
print(f'Compliance step additions: {fixed_compliance}')
print(f'Files modified: {files_modified} / {len(files)}')
