from django.db.models import Q


def build_icontains_query(fields, keyword):
    query = Q()
    if not keyword:
        return query
    for field in fields:
        query |= Q(**{f"{field}__icontains": keyword})
    return query
