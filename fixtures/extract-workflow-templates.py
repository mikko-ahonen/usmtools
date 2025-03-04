import json

with open('workflows.json') as f:
    data = json.load(f)

output = []
workflows = {}
steps = {}

for d in data:
    if d['model'] == 'workflows.account':
        output.append(d)
    if d['model'] == 'workflows.service' and d['fields']['is_global_template']:
        output.append(d)
        service = d['pk']
    if d['model'] == 'workflows.workflow' and d['fields']['is_template']:
        output.append(d)
        workflows[d['pk']] = 1
    if d['model'] == 'workflows.step' and d['fields']['workflow'] in workflows:
        output.append(d)
        steps[d['pk']] = 1
    if d['model'] == 'workflows.activity' and d['fields']['step'] in steps:
        output.append(d)

print(json.dumps(output, indent=2))
