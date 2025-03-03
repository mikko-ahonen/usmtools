import logging

from django_components import component
from compliances.models import Requirement

@component.register("xref_requirement_card")
class XrefRequirementCard(component.Component):
    template_name = "xref/xref_requirement_card.html"

    def get_context_data(self, **kwargs):

        requirement = kwargs["requirement"]
        next_requirement = kwargs["next_requirement"]
        prev_requirement = kwargs["prev_requirement"]
        statuses = Requirement.XREF_STATUSES

        return {
            "statuses": statuses,
            "requirement": requirement,
            "next_requirement": next_requirement,
            "prev_requirement": prev_requirement,
        }

    def get_requirement(self, obj_id):
        try:
            return Requirement.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def get_status(self, target_status):
        for k, v in Requirement.XREF_STATUSES:
            if target_status == k:
                return target_status
        raise ValueError(f"Invalid target status {target_status} for instance of Requirement")

    def post(self, request, obj_id, target_status):
        obj = self.get_requirement(obj_id)
        next_requirement_id = request.POST.get('next_requirement_id', None)
        next_requirement = None
        if next_requirement_id:
            next_requirement = self.get_requirement(next_requirement_id)
        prev_requirement_id = request.POST.get('prev_requirement_id', None)
        prev_requirement = None
        if prev_requirement_id:
            prev_requirement = self.get_requirement(prev_requirement_id)
        status = self.get_status(target_status)
        obj.xref_status = status
        obj.save()
        kwargs = {
            "requirement": obj,
            "next_requirement": next_requirement,
            "prev_requirement": prev_requirement,
        }
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context, slots={}, kwargs=kwargs)
