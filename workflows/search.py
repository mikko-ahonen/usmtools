import re
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramSimilarity
from django.db.models import Case, When, Value, Q, F, CharField
from django.db.models.functions import Collate
from .models import Routine, Profile, OrganizationUnit

TSQUERY_PATTERN = re.compile(r'\s+')

def tsquery(query):
    query = re.sub(TSQUERY_PATTERN, ' ', query)
    clean_query = ''.join(filter(lambda x: x.isalpha() or x.isspace(), query))
    query_terms = clean_query.split()
    tsquery = " & ".join(query_terms)
    if tsquery is None or tsquery == "":
        return None
    tsquery += ":*"
    return SearchQuery(tsquery, search_type="raw")

def search_by_name(cls, search, similarity_threshold=0.38, rank_threshold=0.05, limit_routine_ids=None):
    if search is not None:
        search_query = tsquery(search)
        if search_query:
            search_vector = (SearchVector("name", weight="A"))

            q_match_name = Q(name__istartswith=search)

            q = Q(search=search_query) | Q(match_name=1)
            qs = (cls
                    .objects
                    .annotate(name_similarity=TrigramSimilarity('name', search))
                    .annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
                    .annotate(match_name=Case(
                        When(q_match_name, then=Value(1)),
                        default=Value(0)
                    ))
                    .filter(q)
                    .filter(Q(name_similarity__gt=similarity_threshold) | Q(rank__gt=rank_threshold))
                    .order_by("-match_name", "-rank", "-name_similarity"))

            if limit_routine_ids:
                qs = qs.filter(id__in=limit_routine_ids)
            return qs[0:10]
    return cls.objects.none()

def search_routines(search, similarity_threshold=0.38, rank_threshold=0.05):
    return search_by_name(Routine, search, similarity_threshold=similarity_threshold, rank_threshold=rank_threshold)

def search_organization_units(search, similarity_threshold=0.38, rank_threshold=0.05):
    return search_by_name(OrganizationUnit, search, similarity_threshold=similarity_threshold, rank_threshold=rank_threshold)

def search_profiles(search, similarity_threshold=0.38, rank_threshold=0.05):
    return search_by_name(Profile, search, similarity_threshold=similarity_threshold, rank_threshold=rank_threshold)
