import logging

from django_components import component

from workflows.tenant import current_tenant_id

@component.register("burndown")
class Burndown(component.Component):
    template_name = "burndown/burndown.html"

    def get_context_data(self, **kwargs):

        index = kwargs["index"] 

        #if "board" not in kwargs:
        #    raise ValueError("board required")

        #if "lists" not in kwargs:
        #    raise ValueError("lists required")

        return {
            "index" : index,
        #    "board": kwargs["board"],
        #    "lists": kwargs["lists"],
        #    "tenant_id": tenant_id,
        }


    def get(self, request, *args, **kwargs):
        tenant_id = kwargs['tenant_id']
        op = kwargs['op']

        if op == "start-sprint":
            context = self.start_sprint(tenant_id, request)
        elif op == "end-sprint":
            context = self.end_sprint(tenant_id, request)
        else:
            raise ValueError(f"Invalid op: {op}")

        return self.render_to_response(kwargs=context)

    class Media:
        js = "burndown/burndown.js"
