from django.core.paginator import Paginator as P, EmptyPage


def paginator(datas, page, limit):
    p = P(datas, limit)
    try:
        feeds_paginator = p.page(page)
    except EmptyPage:
        feeds_paginator = p.page(p.num_pages)

    paginator_dict = {
        "total": p.count,
        "num_pages": p.num_pages,
        "has_next": feeds_paginator.has_next(),
        "page": page
    }

    return feeds_paginator, paginator_dict
