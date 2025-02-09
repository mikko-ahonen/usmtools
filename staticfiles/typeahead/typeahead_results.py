import re
import uuid
from django_components import component
from workflows.tenant import current_tenant_id

from workflows.search import search_routines

from django.db.models import Q
from taggit.models import Tag
from workflows.search import search_routines

def is_valid_uuid(s):
    try:
        uuid.UUID(str(s))
        return True
    except ValueError:
        return False

@component.register("typeahead_results")
class TypeaheadResults(component.Component):
    template_name = "typeahead/typeahead_results.html"

    def post(self, request, *args, **kwargs):
        q = request.POST.get('q') # query string
        t = request.POST.get('t') # type of search
        if q is None or q == "" or t is None or t == "":
            results = []
        else:
            if t == "r":
                results = [{'id': r.id, 'name': str(r), 'type': 'r'} for r in search_routines(q)]
            elif t == "t":
                results = [{'id': r.id, 'name': r.name, 'type': 't'} for r in Tag.objects.filter(name__startswith=q)]
                print(results)
            else:
                raise ValueError(f"Invalid search type: {t}")

        context = {
            "type": t,
            "results": results,
        }
        return self.render_to_response(context=context, slots={}, kwargs={})

    class Media:
        css = "typeahead/typeahead_results.css"
