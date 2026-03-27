"""Custom pagination with VN thousand-separator in count fields."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.formatters import fmt_vn


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "count_display": fmt_vn(self.page.paginator.count),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "count_display": {"type": "string", "description": "VN-formatted count"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": schema,
            },
        }
