import logging

from django.http import QueryDict

from django_components import component

from workflows.models import Responsibility
from workflows.rasci import RASCI
from workflows.tenant import current_tenant_id
from workflows.tenant_models import tenant_check


@component.register("responsibility_editor")
class ResponsibilityEditor(component.Component):
    template_name = "action/responsibility_editor.html"

    def get_context_data(self, **kwargs):

        responsibility = kwargs.get("responsibility", None)

        if not responsibility:
            raise ValueError("responsibility is required")

        tenant_id = current_tenant_id()

        return {
            "tenant_id": tenant_id,
            "responsibility": responsibility,
        }


    def get_param(self, qd, name):
        v = qd.get(name)
        if v and v != '' and v != 'None':
            return v
        return None

    def post(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()
        tenant_check(request=request, tenant_id=tenant_id)
        responsibility_id = kwargs.get('responsibility_id', None)
        responsibility = Responsibility.objects.get(id=responsibility_id)
        qd = QueryDict(request.body)
        rtype = self.get_param(qd, 'rtype')
        rtype_checked = self.get_param(qd, 'responsibility-checkbox')

        if rtype_checked:
            responsibility.types = RASCI(responsibility.types).add_types(rtype).get_types()
        else:
            responsibility.types = RASCI(responsibility.types).remove_types(rtype).get_types()
        responsibility.save()

        context = self.get_context_data(responsibility=responsibility)

        return self.render_to_response(context=context, slots={}, kwargs={'tenant_id': tenant_id, 'responsibility': responsibility})

