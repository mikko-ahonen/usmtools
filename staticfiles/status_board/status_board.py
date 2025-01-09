import logging

from django_components import component, types
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

@component.register("status_board")
class StatusBoard(component.Component):
    template_name = "status_board/status_board.html"

    columns = {
        'non-compliant': {
            'name': _("Non-compliant"),
            'statuses': ['new', 'implemented', 'non-compliant', 'failed'],
            'target_status': 'non-compliant',
        },
        'compliant': {
            'name': _("Compliant"),
            'statuses': ['compliant'],
            'target_status': 'compliant',
        },
        'audited': {
            'name': _("Audited"),
            'statuses': ['audited'],
            'target_status': 'audited',
        },
    }

    def get_context_data(self, **kwargs):
        root_id = None
        if "root_id" in kwargs:
            root_id = kwargs["root_id"]
        else:
            if "root" in kwargs:
                root_id = kwargs["root"].id
            else:
                raise ValueError("root or root_id required")
        if "entities" not in kwargs:
            raise ValueError("entities required")
        #from pudb.remote import set_trace; set_trace(term_size=(160, 40), host='0.0.0.0', port=6900)
        return {
            "root_id": root_id,
            "columns": self.columns,
            "entities": kwargs.get("entities", []),
        }

    def post(self, request, *args, **kwargs):
        qd = QueryDict(request.body)
        root_id = kwargs['root_id']
        column_slug = kwargs['column_slug']
        column = self.columns[column_slug]
        target_status = column['target_status']
        for index, eid in enumerate(qd['id']):
            try:
                entity = entities.get(id=eid)
            except ObjectDoesNotExist:
                entity = Domain.objects.filter(section__requirement__constraint_id=eid)
                entity.status = target_status
            entity.index = index
            entity.save()
        context = self.get_context_data(entities=Constraint.objects.filter(requirement__section__domain_id=root_id), root_id=root_id)
        return self.render_to_response(context)

    class Media:
        js = "status_board.js"
        css = "status_board.css"

