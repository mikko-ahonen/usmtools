import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref_status_transitions")
class XrefStatusTransitions(component.Component):
    template_name = "xref/xref_status_transitions.html"

    def get_context_data(self, **kwargs):

        obj = kwargs["obj"]

        return {
            "obj": obj,
        }

    def get_obj_class(self, obj_type):
        if obj_type == 'Statement':
            return Statement
        elif obj_type == 'Constraint':
            return Constraint
        elif obj_type == 'Requirement':
            return Requirement

        raise ValueError("Invalid object type: {obj_type}")

    def get_object(self, obj_type, obj_id):
        obj_class = self.get_obj_class(obj_type)
        try:
            return obj_class.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def get_status(self, obj_type, target_status):
        obj_class = self.get_obj_class(obj_type)
        for k, v in obj_class.XREF_STATUSES:
            if target_status == k:
                return target_status
        raise ValueError(f"Invalid target status {target_status} for instance of {obj_class.__name__}")

    def post(self, request, obj_type, obj_id, target_status):
        obj = self.get_object(obj_type, obj_id)
        status = self.get_status(obj_type, target_status)
        obj.xref_status = status
        obj.save()
        context = self.get_context_data(obj=obj)
        response = self.render_to_response(context=context, slots={}, kwargs={'obj': obj})
        response['HX-Refresh'] = 'true'
        response['Access-Control-Expose-Headers'] = 'HX-Refresh'
        return response 
