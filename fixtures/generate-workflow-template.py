import json
import uuid
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)


    workflow_uuid = uuid.uuid4()
    name = data['name']
    print (f"""
{{
    "model": "workflows.workflow",
    "pk": "{workflow_uuid}",
    "fields": {{
        "service": "69fea6d9-bf2c-4eb6-9605-1a78145b9549",
        "name": "{name}",
        "is_template": true
    }},
}},""")
    for idx, step in enumerate(data['steps'], start=1):
        u = uuid.uuid4()
        print (f"""{{
    "model": "workflows.step",
    "pk": "{u}",
    "fields": {{
        "index": {idx},
        "name": "{step['name']}",
        "description": "{step['description']}",
        "workflow": "{workflow_uuid}",
        "process": "{step['process']}"
    }}
}},""")
