import uuid
import json

with open('workflow-templates-fi-in.json') as f:
    data = json.load(f)

lang = 'fi'
output = []
workflows = {}
steps = {}

for d in data:
    if d['model'] == 'workflows.routine' and d['fields']['is_template']:
        u = str(uuid.uuid4())
        workflows[d['pk']] = u
        d['pk'] = u
        d['lang'] = lang
        output.append(d)
    if d['model'] == 'workflows.step' and d['fields']['routine'] in workflows:
        u = str(uuid.uuid4())
        steps[d['pk']] = u
        d['pk'] = u
        d['fields']['routine'] = workflows[d['fields']['routine']]
        output.append(d)
    if d['model'] == 'workflows.activity' and d['fields']['step'] in steps:
        u = str(uuid.uuid4())
        d['pk'] = u
        output.append(d)

print(json.dumps(output, indent=2))
