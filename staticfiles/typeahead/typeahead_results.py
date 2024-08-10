#import logging
from django_components import component

from cal.search import search_venues, search_municipalities, search_compositions, search_performers, search_regions

#logger = logging.getLogger(__name__)

@component.register("typeahead_results")
class TypeaheadResults(component.Component):
    template_name = "typeahead/typeahead_results.html"

    def post(self, request, *args, **kwargs):
        q = self.request.POST.get('q') # query string
        t = self.request.POST.get('t') # type of search
        if q is None or q == "" or t is None or t == "":
            results = []
        else:
            if t == "v":
                results = [{'id': r.id, 'name': str(r), 'type': 'v'} for r in search_venues(q)]
            elif t == "m":
                results = [{'id': r.id, 'name': str(r), 'type': 'm'} for r in search_municipalities(q)]
            elif t == "r":
                results = [{'id': r.id, 'name': str(r), 'type': 'r'} for r in search_regions(q)]
            elif t == "cp":
                results = [{'id': r.id, 'name': r.derived_name, 'type': 'c', 'type_name': 'Kokoonpano', 'description': r.description} for r in search_compositions(q)]
                results.extend([{'id': r.id, 'name': str(r), 'type': 'p', 'type_name': 'Esiintyjä'} for r in search_performers(q)])
            else:
                raise ValueError(f"Invalid search type: {t}")

        context = {
            "type": t,
            "results": results,
        }
        return self.render_to_response(context, {})

    class Media:
        css = "typeahead/typeahead_results.css"
