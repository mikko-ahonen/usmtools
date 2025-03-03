import logging

from django_components import component
from compliances.models import Statement

@component.register("xref_statement_card")
class XrefStatementCard(component.Component):
    template_name = "xref/xref_statement_card.html"

    def get_context_data(self, **kwargs):

        statement = kwargs["statement"]
        next_statement = kwargs["next_statement"]
        prev_statement = kwargs["prev_statement"]
        statuses = Statement.XREF_STATUSES

        return {
            "statuses": statuses,
            "statement": statement,
            "next_statement": next_statement,
            "prev_statement": prev_statement,
        }

    def get_statement(self, obj_id):
        try:
            return Statement.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def get_status(self, target_status):
        for k, v in Statement.XREF_STATUSES:
            if target_status == k:
                return target_status
        raise ValueError(f"Invalid target status {target_status} for instance of Statement")

    def post(self, request, obj_id, target_status):
        obj = self.get_statement(obj_id)
        next_statement_id = request.POST.get('next_statement_id', None)
        next_requirement = None
        if next_statement_id:
            next_statement = self.get_statement(next_statement_id)
        prev_statement_id = request.POST.get('prev_statement_id', None)
        prev_statement = None
        if prev_statement_id:
            prev_statement = self.get_statement(prev_statement_id)
        status = self.get_status(target_status)
        obj.xref_status = status
        obj.save()
        kwargs = {
            "statement": obj,
            "next_statement": next_statement,
            "prev_statement": prev_statement,
        }
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context, slots={}, kwargs=kwargs)
